from abc import ABC, abstractmethod
from typing import Any, Optional, Union, Tuple, List

from .schema import RGB_ndarray_img, FaceBase, EntryExitRawDBCreate, EntryExitRaw, EntryExit


class BaseCamera(ABC):
    @property
    @abstractmethod
    def frame_width(self):
        pass

    @property
    @abstractmethod
    def frame_height(self):
        pass

    @abstractmethod
    def get_flame(self) -> Tuple[Optional[RGB_ndarray_img], ...]:
        pass


class BaseFaceDetection(ABC):
    @property
    @abstractmethod
    def resolution_zoom(self) -> Optional[float]:
        """
        :param resolution_zoom: (0,1]の範囲で元画像の解像度を圧縮する。数字が小さいほど処理が軽い。\n
        """

        # detect_faceはこのプロパティを使って実現するべき
        pass

    @property
    @abstractmethod
    def range_zoom(self) -> Optional[Tuple[int, ...]]:
        """
        :param range_zoom: FaceBaseの顔の境界ボックスを拡大あるいは縮小する。\n
        値が 1 つ場合、全四辺に同じ値でズームする。\n
        値が 2 つ場合、1 つ目は上下、2 つ目は左右に適用される。\n
        値が 3 つ場合、1 つ目は上、2 つ目は左右、3 つ目は下の辺に適用される。\n
        値が 4 つ場合、それぞれ上、右、下、左の順 (時計回り) に適用される。\n
        """

        # detect_faceはこのプロパティを使って実現するべき
        pass

    @abstractmethod
    def detect_face(self, img: RGB_ndarray_img) -> List[FaceBase]:
        """
        画像内の顔の境界ボックスとを返す。この時点でわかる場合、顔の方向も返す。
        """
        pass


class BaseFaceIdentification(ABC):
    @property
    @abstractmethod
    def model(self):
        pass

    @model.setter
    @abstractmethod
    def model(self, val):
        pass

    @abstractmethod
    def identify_face(self, face_img: RGB_ndarray_img) -> Union[int, str]:
        """
        It shoule return a name or id that can identify someone.
        誰かを識別できる名前(str)またはIDを返すはず。
        """
        pass


class BaseEntryExitJudgement(ABC):
    @abstractmethod
    def judge_entry_exit(
        self,
        entry_exit_raw_list: List[EntryExitRaw],
    ) -> List[EntryExit]:
        """
        一連のEntryExitRawデータから、誰がいつ入室/退室したかを返す。
        """
        pass


class BaseEntryExitIO(ABC):
    @property
    @abstractmethod
    def raw_db_path(self):
        pass

    @property
    @abstractmethod
    def db_path(self):
        pass

    @abstractmethod
    def save_entry_exit_raw(self, entry_exit_db: EntryExitRawDBCreate) -> Any:
        """
        EntryExitRaw（ローデータ）をraw_db_pathに保存する。
        """

        # ローカルファイルに保存するか、データベースに保存するかは自由
        pass

    @abstractmethod
    def save_entry_exit(self, entry_exit_db_list: EntryExit) -> Any:
        """
        EntryExitBase（入退室情報）をdb_pathに保存する。
        """

        # ローカルファイルに保存するか、データベースに保存するかは自由
        pass

    @abstractmethod
    def encode_img(self, img) -> str:
        pass

    @abstractmethod
    def decode_img(self, str) -> RGB_ndarray_img:
        pass
