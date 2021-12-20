import asyncio
from datetime import datetime
from typing import List, Tuple, Callable, Optional
from copy import deepcopy
import logging

import cv2

from abc_classes import BaseCamera, BaseFaceDetection, BaseFaceIdentification, BaseEntryExitIO, BaseEntryExitJudgement
from schema import RGB_ndarray_img, FaceBase, EntryExitRaw, EntryExitRawDBCreate, SchedulerConfig
import message

err_msg = message.err
log_msg = message.log


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
            raise TypeError(err_msg.type % "SchedulerConfig", type(config))

        # 処理系obj、関数
        if isinstance(callback, Callable):
            raise TypeError(err_msg.type % "Callable", type(callback))
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
        if isinstance(trigger, Callable):
            raise TypeError(err_msg.type % "Callable", type(trigger))
        self._trigger = trigger

        self.loop_func = {
            "async": self.async_loop,
            "sync": self.sync_loop,
        }
        self.logger.info("Schedulerがインスタンス化されました")

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
        frame_width: int,
        frame_height: int,
    ):
        if isinstance(self.f_identify, BaseFaceIdentification):
            if face_list:
                ee_raw_list = self.f_identify.identify_face_base_list(
                    frame,
                    time,
                    face_list,
                    frame_width,
                    frame_height,
                )

                for ee_rew in ee_raw_list:
                    face_img = frame[ee_rew.top:ee_rew.bottom, ee_rew.left:ee_rew.right]
                    self.eeio.save_entry_exit_raw(
                        EntryExitRawDBCreate(
                            **ee_rew.dict(),
                            img_base64=self.eeio.encode_img(face_img),
                        )
                    )

            return ee_raw_list

        else:
            self.callback(
                called_func="__scheduled_judge_entry_exit",
                frame=frame,
                time=time,
                face_list=time,
            )

    def __scheduled_judge_entry_exit(self, entry_exit_raw_list: List[EntryExitRaw]):
        if isinstance(self.ee_judge, BaseEntryExitJudgement):
            if entry_exit_raw_list:
                ee_list = self.ee_judge.judge_entry_exit(entry_exit_raw_list)
                if ee_list:
                    self.eeio.save_entry_exit(ee_list)
                    self.ee_raw_list = []
                return ee_list
        else:
            self.callback(
                called_func="__scheduled_judge_entry_exit",
                entry_exit_raw_list=entry_exit_raw_list,
            )

    async def __process(self, unprocessed_frame_list):
        all_ee_raw_list = []
        for frame, time_now in unprocessed_frame_list:
            if self.trigger_flag:
                await asyncio.sleep(5)

            face_list = self.__scheduled_detect_face(frame)
            self.logger.debug("face_list: " + str(face_list))
            await asyncio.sleep(0.001)

            ee_raw_list = self.__scheduled_identify_face(
                frame,
                time_now,
                face_list,
                self.cam.frame_width,
                self.cam.frame_height,
            )
            self.logger.debug("ee_raw_list: " + str(ee_raw_list))

            all_ee_raw_list += ee_raw_list
            await asyncio.sleep(0.001)

        ee_list = self.__scheduled_judge_entry_exit(all_ee_raw_list)
        self.logger.info("ee_list=%s" % str(ee_list))

    async def async_loop(self) -> None:

        trigger_flag = False
        trigged_time = datetime.min
        unprocessed_frame_list = []
        now_task = asyncio.get_event_loop().create_future()
        now_task.set_result(None)

        while True:
            frame = self.cam.get_flame()[0]
            time_now = datetime.now()

            if self._trigger(frame):
                # trigger発動するとframeをひたすら貯まる
                trigger_flag = True
                trigged_time = datetime.now()
                self.logger.info("%s トリガーが発動されました" % datetime.now().strftime("%x %X"))

            if trigger_flag:
                unprocessed_frame_list.append((frame, time_now))

                # triggerが一定時間反応がなかったらtrigger_flagを折る
                passed_time = (datetime.now() - trigged_time).total_seconds
                if passed_time > self.config.motion_done_after_sec:
                    trigger_flag = False
                    self.logger.info("トリガーが解放されました、%dフレームが溜まっています" % len(unprocessed_frame_list))  # yapf:disable

            # trigger_flagが立っていない時は溜まったframeを処理する
            elif now_task.done() and unprocessed_frame_list:
                self.logger.info("新しいprocessを開始します")
                now_task = asyncio.create_task(
                    self.__process(deepcopy(unprocessed_frame_list))
                )
                unprocessed_frame_list = []

            await asyncio.sleep(1 / int(self.config.trigger_rate * 1.2))

    def sync_loop(self) -> None:

        ee_raw_list = []
        last_detected_time = datetime.now()

        while True:
            frame = self.cam.get_flame()[0]
            time_now = datetime.now()

            face_list = self.__scheduled_detect_face(frame)
            if face_list:
                last_detected_time = time_now

            ee_raw_list = self.__scheduled_identify_face(
                frame,
                time_now,
                face_list,
                self.cam.frame_width,
                self.cam.frame_height,
            )

            # 動きが終わるまで一旦保存
            ee_raw_list += ee_raw_list

            passed_time = (datetime.now() - last_detected_time).total_seconds
            if passed_time > self.config.motion_done_after_sec and ee_raw_list:
                ee_list = self.__scheduled_judge_entry_exit(ee_raw_list)
                ee_raw_list = []
                if ee_list:
                    self.eeio.save_entry_exit(ee_list)

    def start(self, loop_func=None, mode="async") -> None:
        if loop_func is None:
            loop_func = self.loop_func[mode]
            self.logger.info("`loop_func`はNone、デフォルトのloop_funcを使用する")

        if mode == "async":
            asyncio.run(loop_func(), debug=self.debug)
        elif mode == "sync":
            loop_func()
        self.logger.info("`mode=%s`で処理開始......")


class Cv2Camera(BaseCamera):
    def __init__(
        self,
        device_id: int = 1,
        path: Optional[str] = None,
        frame_width: int = 1280,
        frame_height: int = 720,
        fps: int = 30
    ) -> None:
        if path:
            self.cam = cv2.VideoCapture(path)
        else:
            self.cam = cv2.VideoCapture(device_id)
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
            self.cam.set(cv2.CAP_PROP_FPS, fps)

        self._frame_width = cv2.get(cv2.CAP_PROP_FRAME_WIDTH)
        self._frame_height = cv2.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = cv2.get(cv2.CAP_PROP_FPS)

    @property
    def frame_width(self):
        return self._frame_width

    @property
    def frame_height(self):
        return self._frame_height

    def get_flame(self) -> Tuple[RGB_ndarray_img, ...]:
        ret, frame = self.cam.read()
        return frame, ret


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
