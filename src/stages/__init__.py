"""Stages package for the autonomous video pipeline."""

from src.stages.base import BaseStage
from src.stages.stage_1_topic import TopicSelectionStage
from src.stages.stage_2_script import ScriptResearchStage
from src.stages.stage_3_voiceover import VoiceoverStage
from src.stages.stage_4_visuals import VisualsStage
from src.stages.stage_5_assembly import VideoAssemblyStage
from src.stages.stage_6_metadata import MetadataThumbnailStage
from src.stages.stage_7_uploader import YouTubeUploadStage

__all__ = [
    "BaseStage",
    "TopicSelectionStage",
    "ScriptResearchStage",
    "VoiceoverStage",
    "VisualsStage",
    "VideoAssemblyStage",
    "MetadataThumbnailStage",
    "YouTubeUploadStage",
]
