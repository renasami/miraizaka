from typing import List

from starlette.requests import Request

from face_ee_manager.abc_classes import BaseFaceIdentification, BaseEntryExitJudgement
from face_ee_manager.schema import RGB_ndarray_img, EntryExitRaw, EntryExit, Direction, EEAction


def get_db(request: Request):
    return request.state.db


class FaceIdentification(BaseFaceIdentification):
    @property
    def model(self):
        pass

    @model.setter
    def model(self, val):
        pass

    def identify_face(self, face_img: RGB_ndarray_img):
        return 7


class EntryExitJudgement(BaseEntryExitJudgement):
    def judge_entry_exit(
        self,
        entry_exit_raw_list: List[EntryExitRaw],
    ) -> List[EntryExit]:

        ee_raw_name_dict: dict[str, List[EntryExitRaw]] = {}
        for ee_raw in entry_exit_raw_list:
            if ee_raw.identification in ee_raw_name_dict:
                ee_raw_name_dict[ee_raw.identification].append(ee_raw)
            else:
                ee_raw_name_dict[ee_raw.identification] = [ee_raw]

        res = []
        for key, ee_raw_list in ee_raw_name_dict.items():
            right_face = 0
            left_face = 0
            for ee_raw in ee_raw_list:
                if ee_raw.direction == Direction.LEFT_FACE:
                    left_face += 1
                elif ee_raw.direction == Direction.RIGHT_FACE:
                    right_face += 1

            if right_face - left_face > 0:
                # right face
                res.append(
                    EntryExit(
                        datetime=ee_raw_list[0].datetime,
                        identify_id=key,
                        action=EEAction.EXIT
                    )
                )
            else:
                # left face
                res.append(
                    EntryExit(
                        datetime=ee_raw_list[0].datetime,
                        identify_id=key,
                        action=EEAction.ENTRY
                    )
                )

        return res
