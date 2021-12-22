import asyncio
from datetime import datetime
from typing import List, Callable, Optional
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
        face_identification_obj: Optional[BaseFaceIdentification] = None,
        entry_exit_judgement_obj: Optional[BaseEntryExitJudgement] = None,
        trigger: Callable[[RGB_ndarray_img], bool] = None,
        callback: Optional[Callable] = None,
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

        if type(config) == dict:
            self.config = SchedulerConfig(**config)
        elif isinstance(config, SchedulerConfig):
            self.config = config
        else:
            raise TypeError(err_msg.type % ("SchedulerConfig", type(config)))

        # 処理系obj、関数
        if not callable(callback):
            raise TypeError(err_msg.type % ("Callable", type(callback)))
        self.callback = callback

        if not isinstance(camera_obj, BaseCamera):
            raise NameError(err_msg.scheduler_name % str(BaseCamera))
        self.cam = camera_obj

        if not isinstance(entry_exit_io_obj, BaseEntryExitIO):
            raise NameError(err_msg.scheduler_name % str(BaseEntryExitIO))
        self.eeio = entry_exit_io_obj

        self.f_detect = face_detection_obj
        self.f_identify = face_identification_obj
        self.ee_judge = entry_exit_judgement_obj

        # async_loop用プロパティ
        if trigger is None:
            self._trigger = self._build_in_trigger
        elif not callable(trigger):
            raise TypeError(err_msg.type % ("Callable", type(trigger)))
        self._trigger = trigger
        self.trigger_flag = False

        self.loop_func = {
            "async": self.async_loop,
            "sync": self.sync_loop,
        }
        self.logger.info("Schedulerがインスタンス化されました")

    def _build_in_trigger(self):
        ...

    def __scheduled_detect_face(self, frame: RGB_ndarray_img):
        if isinstance(self.f_detect, BaseFaceDetection):
            return self.f_detect.detect_face(frame)
        else:
            raise NameError(err_msg.scheduler_name % str(BaseFaceDetection))

    def __scheduled_identify_face(
        self,
        frame: RGB_ndarray_img,
        time: datetime,
        face_list: List[FaceBase],
    ) -> List[EntryExitRaw]:
        if not isinstance(self.f_identify, BaseFaceIdentification):
            self.callback(
                called_func="__scheduled_identify_face",
                frame=frame,
                time=time,
                face_list=face_list,
            )
            return []

        ee_raw_list = []
        for face in face_list:
            face_img = frame[face.top:face.bottom, face.left:face.right]
            id = self.f_identify.identify_face(face_img)

            ee_raw = EntryExitRaw(
                datetime=time,
                *face.dict(),
                identification=id,
            )

            ee_raw_list.append(ee_raw)

        return ee_raw_list

    def __scheduled_judge_entry_exit(self, entry_exit_raw_list: List[EntryExitRaw]):
        if not isinstance(self.ee_judge, BaseEntryExitJudgement):
            self.callback(
                called_func="__scheduled_judge_entry_exit",
                entry_exit_raw_list=entry_exit_raw_list,
            )
            return []

        ee_list = []
        if entry_exit_raw_list:
            ee_list = self.ee_judge.judge_entry_exit(entry_exit_raw_list)
            if ee_list:
                self.eeio.save_entry_exit(ee_list)
                self.ee_raw_list = []

        return ee_list

    async def __process(self, unprocessed_frame_list):
        all_ee_raw_list = []
        for frame, time_now in unprocessed_frame_list:
            if self.trigger_flag:
                await asyncio.sleep(5)

            # 顔検出
            face_list = self.__scheduled_detect_face(frame)
            if face_list:
                self.logger.info("%d人が検出されました" % len(face_list))
                self.logger.debug("face_list: " + str(face_list))
            await asyncio.sleep(0.001)

            # 顔識別
            param = (frame, time_now, face_list)
            ee_raw_list = self.__scheduled_identify_face(*param)
            if ee_raw_list:
                self.logger.debug("ee_raw_list: " + str(ee_raw_list))
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
        ee_list = self.__scheduled_judge_entry_exit(all_ee_raw_list)
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
            if frame is None:
                break
            time_now = datetime.now()

            face_list = self.__scheduled_detect_face(frame)
            if face_list:
                last_detected_time = time_now
                self.logger.info("%d人が検出されました" % len(face_list))
                self.logger.debug("face_list: " + str(face_list))

            param = (frame, time_now, face_list)
            ee_raw_list = self.__scheduled_identify_face(*param)
            if ee_raw_list:
                self.logger.debug("ee_raw_list: " + str(ee_raw_list))

            # 保存raw
            for ee_raw in ee_raw_list:
                face_img = frame[ee_raw.top:ee_raw.bottom, ee_raw.left:ee_raw.right]
                img_base64 = self.eeio.encode_img(face_img)
                eer_db = EntryExitRawDBCreate(**ee_raw.dict(), img_base64=img_base64)
                self.eeio.save_entry_exit_raw(eer_db)

            # 動きが終わるまで一旦保存
            ee_raw_list += ee_raw_list

            for face in face_list:
                cv2.rectangle(frame[:, :, ::-1], (face.left, face.top), (face.right, face.bottom), (0, 0, 255), 2)
            cv2.imshow('Video', frame[:, :, ::-1])
            cv2.waitKey(0)

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
        if mode == "async":
            asyncio.run(loop_func(), debug=self.debug)
        elif mode == "sync":
            loop_func()


# for ee_rew in ee_raw_list:
#     face_img = frame[ee_rew.top:ee_rew.bottom, ee_rew.left:ee_rew.right]

#     img_base64 = self.eeio.encode_img(face_img)
#     eer_db = EntryExitRawDBCreate(**ee_rew.dict(), img_base64=img_base64)
#     self.eeio.save_entry_exit_raw(eer_db)

# raw_list: List[EntryExitRaw] = []

# for face in face_list:
#     # 顔取り出し
#     face_img = frame[face.top:face.bottom, face.left:face.right]
#     # 識別
#     id = self.f_identify.identify_face(face_img)
#     # データ整形
#     entry_exit_raw = EntryExitRaw(
#         datetime=time,
#         *face.dict(),
#         identification=id,
#         frame_width=self.cam.frame_width,
#         frame_height=self.cam.frame_height,
#     )
#     raw_list.append(entry_exit_raw)
#     # 保存
#     self.eeio.save_entry_exit_raw(
#         EntryExitRawDBCreate(
#             **entry_exit_raw.dict(),
#             img_base64=self.eeio.encode_img(face_img),
#         )
#     )

# return raw_list

# raw_list = []

# for frame, time_now in unprocessed_frame_list:
#     if self.trigger_flag:
#         await asyncio.sleep(5)

#     face_list = self.f_detect.detect_face(frame)

#     for face in face_list:
#         if self.trigger_flag:
#             await asyncio.sleep(5)
#         # 顔を取り出す
#         face_img = frame[face.top:face.bottom, face.left:face.right]
#         # 識別する
#         id = self.f_identify.identify_face(face_img)

#         entry_exit_raw = EntryExitRaw(
#             datetime=time_now,
#             *face.dict(),
#             identification=id,
#             frame_width=self.cam.frame_width,
#             frame_height=self.cam.frame_height,
#         )

#         raw_list.append(entry_exit_raw)
#         self.eeio.save_entry_exit_raw(
#             EntryExitRawDBCreate(
#                 **entry_exit_raw.dict(),
#                 img_base64=self.eeio.encode_img(face_img),
#             )
#         )
#         await asyncio.sleep(0.001)
#     await asyncio.sleep(0.001)

# ee_list = self.ee_judge.judge_entry_exit(raw_list)
# if ee_list:
#     self.eeio.save_entry_exit(ee_list)
