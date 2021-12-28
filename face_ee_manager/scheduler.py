import asyncio
from datetime import datetime
from typing import List, Callable
from copy import deepcopy
import logging

import cv2

from .abc_classes import BaseCamera, BaseFaceDetection, BaseFaceIdentification, BaseEntryExitIO, BaseEntryExitJudgement
from .schema import RGB_ndarray_img, FaceBase, EntryExitRaw, EntryExitRawDBCreate, SchedulerConfig
from . import message

err_msg = message.err
log_msg = message.log


class StopProcess(Exception):
    def __init__(self, val) -> None:
        self.val = val


class Scheduler:
    def __init__(
        self,
        camera_obj: BaseCamera,
        entry_exit_io_obj: BaseEntryExitIO,
        face_detection_obj: BaseFaceDetection,
        face_identification_obj: BaseFaceIdentification,
        entry_exit_judgement_obj: BaseEntryExitJudgement,
        trigger: Callable[[RGB_ndarray_img], bool],
        config: SchedulerConfig = SchedulerConfig(),
        debug: bool = False,
    ) -> None:

        self.logger = logging.getLogger("Scheduler")
        self.logger.setLevel(logging.INFO)
        self.logger.info("Schedulerを初期化しています......")

        self.debug = debug
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
            logging.getLogger("asyncio").setLevel(logging.DEBUG)

        if type(config) == dict: self.config = SchedulerConfig(**config)
        elif isinstance(config, SchedulerConfig): self.config = config
        else: raise TypeError(err_msg.type % ("SchedulerConfig", type(config)))

        # 処理系obj
        obj_param = [
            (camera_obj, BaseCamera),
            (entry_exit_io_obj, BaseEntryExitIO),
            (face_detection_obj, BaseFaceDetection),
            (face_identification_obj, BaseFaceIdentification),
            (entry_exit_judgement_obj, BaseEntryExitJudgement),
        ]

        for input_obj, obj_class in obj_param:
            if not isinstance(input_obj, obj_class):
                raise NameError(err_msg.type % (str(obj_class), type(input_obj)))

        self.cam = camera_obj
        self.eeio = entry_exit_io_obj
        self.fd = face_detection_obj
        self.fi = face_identification_obj
        self.eej = entry_exit_judgement_obj

        # async_loop用プロパティ
        if not callable(trigger):
            raise TypeError(err_msg.type % ("Callable", type(trigger)))
        self._trigger = trigger
        self.trigger_flag = False

        self.loop_func = {
            "async": self.async_loop,
            "sync": self.sync_loop,
        }
        self.logger.info("Schedulerがインスタンス化されました")

    def __identify_face_and_data_shaping(
        self,
        frame: RGB_ndarray_img,
        time: datetime,
        face_list: List[FaceBase],
    ) -> List[EntryExitRaw]:

        ee_raw_list = []
        for face in face_list:
            face_img = frame[face.top:face.bottom, face.left:face.right]
            id = self.fi.identify_face(face_img)

            ee_raw = EntryExitRaw(
                datetime=time,
                *face.dict(),
                identification=id,
            )

            ee_raw_list.append(ee_raw)

        return ee_raw_list

    async def __process(self, unprocessed_frame_list):
        all_ee_raw_list = []
        ufl = unprocessed_frame_list
        for (frame, time_now), frame_index in zip(ufl, range(len(ufl))):
            if self.trigger_flag: await asyncio.sleep(5)

            # 顔検出
            face_list = self.fd.detect_face(frame)
            if face_list:
                self.logger.info("%d人が検出されました" % len(face_list))
                self.logger.debug("face_list: " + str(face_list))
            await asyncio.sleep(0.001)

            if hasattr(self.eeio, "send_face_list"):
                self.eeio.send_face_list(face_list, time_now, frame, frame_index, len(ufl))  # yapf: disable

            # 顔識別
            param = (frame, time_now, face_list)
            ee_raw_list = self.__identify_face_and_data_shaping(*param)
            if ee_raw_list: self.logger.debug("ee_raw_list: " + str(ee_raw_list))
            all_ee_raw_list += ee_raw_list
            await asyncio.sleep(0.001)

            # 保存raw
            for ee_raw in ee_raw_list:
                face_img = frame[ee_raw.top:ee_raw.bottom, ee_raw.left:ee_raw.right]
                img_base64 = self.eeio.encode_img(face_img)
                eer_db = EntryExitRawDBCreate(**ee_raw.dict(), img_base64=img_base64)
                self.eeio.save_entry_exit_raw(eer_db)
                await asyncio.sleep(0.001)

        # 入退室判別
        ee_list = self.eej.judge_entry_exit(all_ee_raw_list)
        # 保存
        for ee in ee_list:
            self.eeio.save_entry_exit(ee)
            self.logger.info("ee: " + str(ee))

    async def async_loop(self) -> None:

        trigged_time = datetime.min
        unprocessed_frame_list = []
        now_task = asyncio.get_event_loop().create_future()
        now_task.set_result(None)

        while True:
            frame = self.cam.get_flame()[0]
            time_now = datetime.now()

            if self._trigger(frame):
                # trigger発動するとframeをひたすら貯まる
                self.trigger_flag = True
                trigged_time = datetime.now()
                self.logger.info("%s トリガーが発動されました" % datetime.now().strftime("%x %X"))

            if self.trigger_flag:
                unprocessed_frame_list.append((frame, time_now))

                # triggerが一定時間反応がなかったらtrigger_flagを折る
                passed_time = (datetime.now() - trigged_time).total_seconds()
                if passed_time > self.config.motion_done_after_sec:
                    self.trigger_flag = False
                    meg = "トリガーが解放されました、%dフレームが溜まっています" % len(unprocessed_frame_list)
                    self.logger.info(meg)  # yapf:disable

            # trigger_flagが立っていない時は溜まったframeを処理する
            elif now_task.done() and unprocessed_frame_list:
                self.logger.info("新しいprocessを開始します")
                new_task = self.__process(deepcopy(unprocessed_frame_list))
                now_task = asyncio.create_task(new_task)
                unprocessed_frame_list = []

            await asyncio.sleep(1 / int(self.config.trigger_rate * 1.2))

    def sync_loop(self) -> None:

        ee_raw_list = []
        last_detected_time = datetime.now()

        while True:
            frame = self.cam.get_flame()[0]
            if frame is None: break
            time_now = datetime.now()

            face_list = self.__scheduled_detect_face(frame)
            if face_list:
                last_detected_time = time_now
                self.logger.info("%d人が検出されました" % len(face_list))
                self.logger.debug("face_list: " + str(face_list))

            param = (frame, time_now, face_list)
            ee_raw_list = self.__scheduled_identify_face(*param)
            if ee_raw_list: self.logger.debug("ee_raw_list: " + str(ee_raw_list))

            # 保存raw
            for ee_raw in ee_raw_list:
                face_img = frame[ee_raw.top:ee_raw.bottom, ee_raw.left:ee_raw.right]
                img_base64 = self.eeio.encode_img(face_img)
                eer_db = EntryExitRawDBCreate(**ee_raw.dict(), img_base64=img_base64)
                self.eeio.save_entry_exit_raw(eer_db)

            # 動きが終わるまで一旦保存
            ee_raw_list += ee_raw_list

            img = frame[:, :, ::-1]
            for f in face_list:
                cv2.rectangle(img, (f.left, f.top), (f.right, f.bottom), (0, 0, 255), 2)
            cv2.imshow('Video', img)
            cv2.waitKey(10)

            passed_time = (datetime.now() - last_detected_time).total_seconds()
            if passed_time > self.config.motion_done_after_sec and ee_raw_list:
                ee_list = self.__scheduled_judge_entry_exit(ee_raw_list)
                self.logger.info("ee_list=%s" % str(ee_list))
                ee_raw_list = []
                if ee_list:
                    self.eeio.save_entry_exit(ee_list)
                    self.logger.debug("ee_list: " + str(ee_list))

    def start(self, loop_func=None, mode="async") -> None:
        if loop_func is None:
            loop_func = self.loop_func[mode]
            self.logger.info("`loop_func`はNone、デフォルトのloop_funcを使用する")

        self.logger.info("`mode=%s`で処理開始......" % mode)
        if mode == "async": asyncio.run(loop_func(), debug=self.debug)
        elif mode == "sync": loop_func()
