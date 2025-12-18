from abc import ABC, abstractmethod

from foxypack.exceptions import DenialAnalyticsException
from foxypack.foxypack_abc.answers import AnswersAnalysis


class FoxyAnalysis(ABC):
    """Abstract class for analysis media content statistics"""

    @abstractmethod
    def get_analysis(self, url: str) -> AnswersAnalysis:
        raise DenialAnalyticsException(url)
