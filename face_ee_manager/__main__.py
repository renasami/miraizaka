import asyncio
from datetime import datetime
from typing import Callable
from copy import deepcopy

from abc_classes import BaceCamera, BaceFaceDetection, BaceFaceIdentification, BaceEntryExitIO, BaceEntryExitJudgement
from schema import EntryExitRaw, EntryExitRawDBCreate


class Scheduler:
    def __init__(
        self,
        camera_obj: BaceCamera,
        face_detection_obj: BaceFaceDetection,
        face_identification_obj: BaceFaceIdentification,
        entry_exit_judgement_obj: BaceEntryExitJudgement,
        entry_exit_io_obj: BaceEntryExitIO,
        trigger: Callable[[], bool],
        config,
    ) -> None:

        self.config = config
        # motion_done_after_sec
        # trigger_rate

        self.cam = camera_obj
        self.f_detect = face_detection_obj
        self.f_identify = face_identification_obj
        self.ee_judge = entry_exit_judgement_obj
        self.eeio = entry_exit_io_obj

        self._trigger = trigger
        self.trigger_flag = False
        self.trigged_time = datetime.min
        self.unprocessed_frame_list = []
        self.now_task = asyncio.get_event_loop().create_future()
        self.now_task.set_result(None)

        self.ee_raw_list = []
        self.last_detected_time = datetime.now()

        self.loop_func = {
            "async": self.async_loop,
            "sync": self.sync_loop,
        }

    # async def trigger(self, *args, **kwargs):
    #     asyncio.sleep(ああああああ)
    #     return self._trigger(*args, **kwargs)

    async def __process(self, unprocessed_frame_list):
        raw_list = []

        for frame, time_now in unprocessed_frame_list:
            if self.trigger_flag:
                await asyncio.sleep(5)
            face_list = self.f_detect.detect_face(frame)

            for face in face_list:
                if self.trigger_flag:
                    await asyncio.sleep(5)
                # 顔を取り出す
                face_img = frame[face.top:face.bottom, face.left:face.right]
                # 識別する
                id = self.f_identify.identify_face(face_img)

                entry_exit_raw = EntryExitRaw(
                    datetime=time_now,
                    *face.dict(),
                    identification=id,
                    frame_width=self.cam.frame_width,
                    frame_height=self.cam.frame_height,
                )

                raw_list.append(entry_exit_raw)
                self.eeio.save_entry_exit_raw(
                    EntryExitRawDBCreate(
                        **entry_exit_raw, img_base64=self.eeio.encode_img(face_img)
                    )
                )
                await asyncio.sleep(0.001)
            await asyncio.sleep(0.001)

        ee_list = self.ee_judge.jzudge_entry_exit(raw_list)
        if ee_list:
            self.eeio.save_entry_exit(ee_list)

    async def async_loop(self) -> None:
        frame = self.cam.get_flame()[0]
        time_now = datetime.now()

        if self._trigger(frame):
            self.trigger_flag = True
            self.trigged_time = datetime.now()

        if self.trigger_flag:
            self.unprocessed_frame_list.append((frame, time_now))

            passed_time = (datetime.now() - self.trigged_time).total_seconds
            if passed_time > self.config.motion_done_after_sec:
                self.trigger_flag = False

        elif self.now_task.done() and self.unprocessed_frame_list:
            self.now_task = asyncio.create_task(
                self.__process(deepcopy(self.unprocessed_frame_list))
            )
            self.unprocessed_frame_list = []

        await asyncio.sleep(1 / int(self.config.trigger_rate * 1.2))

    def sync_loop(self) -> None:
        frame = self.cam.get_flame()[0]
        time_now = datetime.now()

        face_list = self.f_detect.detect_face(frame)

        for face in face_list:
            self.last_detected_time = time_now

            # 顔を取り出す
            face_img = frame[face.top:face.bottom, face.left:face.right]
            # 識別する
            id = self.f_identify.identify_face(face_img)

            entry_exit_raw = EntryExitRaw(
                datetime=time_now,
                *face.dict(),
                identification=id,
                frame_width=self.cam.frame_width,
                frame_height=self.cam.frame_height,
            )

            # 動きが終わるまで一旦保存
            self.ee_raw_list.append(entry_exit_raw)
            self.eeio.save_entry_exit_raw(
                EntryExitRawDBCreate(
                    **entry_exit_raw, img_base64=self.eeio.encode_img(face_img)
                )
            )

        passed_time = (datetime.now() - self.last_detected_time).total_seconds
        if passed_time > self.config.motion_done_after_sec and self.ee_raw_list:

            ee_list = self.ee_judge.judge_entry_exit(self.ee_raw_list)
            if ee_list:
                self.eeio.save_entry_exit(ee_list)
                self.ee_raw_list = []

    def start(self, loop_func=None, mode="async") -> None:
        if loop_func is None:
            loop_func = self.loop_func[mode]

        if mode == "async":
            asyncio.run(loop_func())
        elif mode == "sync":
            loop_func()
