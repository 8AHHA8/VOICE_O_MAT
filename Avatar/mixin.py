from Avatar.sentiment import SentimentMixin
from Avatar.head import HeadMixin
from Avatar.face import FaceMixin
from Avatar.base import BaseMixin

class AvatarMixin(SentimentMixin, HeadMixin, FaceMixin, BaseMixin):
    pass