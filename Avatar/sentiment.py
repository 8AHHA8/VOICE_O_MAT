import time

class SentimentMixin:
    def _current_sentiment(self):
        if getattr(self.audio_gen, 'is_preview', False):
            return getattr(self.audio_gen, 'preview_sentiment', 0.0)

        sentiments = getattr(self.audio_gen, 'segment_sentiments', None)
        durations = getattr(self.audio_gen, 'segment_durations', None)
        start = getattr(self.audio_gen, 'rms_start_time', 0.0)

        if not sentiments or not durations or start <= 0:
            return 0.0

        elapsed = time.time() - start
        acc = 0.0
        for dur, sent in zip(durations, sentiments):
            if elapsed <= acc:
                return sent
            acc += dur
        return sentiments[-1] if sentiments else 0.0