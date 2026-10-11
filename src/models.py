"""Data models and schemas for the YouTube Automation Pipeline.

Designed with dual-engine support: uses Pydantic when installed,
or native dataclasses with full API compatibility when in a minimal environment.
"""

import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

if HAS_PYDANTIC:
    class Topic(BaseModel):
        id: str
        tool_name: str
        angle: str = "Beginner to Pro Guide"
        suggested_title: str
        key_points: List[str] = Field(default_factory=list)
        reason: str = "High search demand and practical workflow value"
        score: float = 9.0

    class ScriptSection(BaseModel):
        id: int
        section_type: str = "step"  # hook, overview, step, pro_tips, mistake, cta
        title: str
        narration: str
        visual_description: str
        image_prompt: str
        on_screen_text: List[str] = Field(default_factory=list)
        duration_estimate_sec: float = 30.0

    class VideoScript(BaseModel):
        topic_id: str
        tool_name: str
        target_duration_minutes: int
        word_count: int
        sections: List[ScriptSection] = Field(default_factory=list)
        full_text: str = ""

    class AudioAsset(BaseModel):
        section_id: int
        file_path: str
        duration_sec: float

    class VisualAsset(BaseModel):
        scene_id: int
        file_path: str
        prompt: str
        duration_sec: float

    class ChapterMarker(BaseModel):
        title: str
        timestamp_seconds: float
        timestamp_formatted: str

    class VideoMetadata(BaseModel):
        title: str
        description: str
        tags: List[str] = Field(default_factory=list)
        category_id: str = "28"
        privacy_status: str = "private"
        chapters: List[ChapterMarker] = Field(default_factory=list)
        ai_disclosure: bool = True

    class ProjectState(BaseModel):
        project_id: str
        current_stage: int = 1
        status: str = "initialized"  # initialized, in_progress, review_ready, completed, failed
        error_message: Optional[str] = None
        created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
        updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

        topic: Optional[Topic] = None
        script: Optional[VideoScript] = None
        audio_assets: List[AudioAsset] = Field(default_factory=list)
        master_audio_path: Optional[str] = None
        visual_assets: List[VisualAsset] = Field(default_factory=list)
        timeline_json_path: Optional[str] = None
        subtitles_path: Optional[str] = None
        final_video_path: Optional[str] = None
        thumbnail_path: Optional[str] = None
        metadata: Optional[VideoMetadata] = None
        youtube_video_id: Optional[str] = None
        youtube_video_url: Optional[str] = None

        def update_timestamp(self) -> None:
            self.updated_at = datetime.now(timezone.utc).isoformat()

else:
    from dataclasses import dataclass, field, asdict

    class CompatibleBase:
        def model_dump(self) -> Dict[str, Any]:
            return asdict(self)

        def model_dump_json(self, indent: int = 2) -> str:
            return json.dumps(self.model_dump(), indent=indent)

        @classmethod
        def model_validate(cls, data: Dict[str, Any]):
            # Handle nested conversions
            return cls(**data)

    @dataclass
    class Topic(CompatibleBase):
        id: str
        tool_name: str
        suggested_title: str
        angle: str = "Beginner to Pro Guide"
        key_points: List[str] = field(default_factory=list)
        reason: str = "High search demand and practical workflow value"
        score: float = 9.0

        @classmethod
        def model_validate(cls, data: Dict[str, Any]):
            return cls(
                id=data.get("id", ""),
                tool_name=data.get("tool_name", ""),
                suggested_title=data.get("suggested_title", ""),
                angle=data.get("angle", "Beginner to Pro Guide"),
                key_points=data.get("key_points", []),
                reason=data.get("reason", "High search demand"),
                score=float(data.get("score", 9.0))
            )

    @dataclass
    class ScriptSection(CompatibleBase):
        id: int
        section_type: str
        title: str
        narration: str
        visual_description: str
        image_prompt: str
        on_screen_text: List[str] = field(default_factory=list)
        duration_estimate_sec: float = 30.0

        @classmethod
        def model_validate(cls, data: Dict[str, Any]):
            return cls(
                id=data.get("id", 0),
                section_type=data.get("section_type", "step"),
                title=data.get("title", ""),
                narration=data.get("narration", ""),
                visual_description=data.get("visual_description", ""),
                image_prompt=data.get("image_prompt", ""),
                on_screen_text=data.get("on_screen_text", []),
                duration_estimate_sec=float(data.get("duration_estimate_sec", 30.0))
            )

    @dataclass
    class VideoScript(CompatibleBase):
        topic_id: str
        tool_name: str
        target_duration_minutes: int
        word_count: int
        sections: List[ScriptSection] = field(default_factory=list)
        full_text: str = ""

        @classmethod
        def model_validate(cls, data: Dict[str, Any]):
            sections = [ScriptSection.model_validate(s) for s in data.get("sections", [])]
            return cls(
                topic_id=data.get("topic_id", ""),
                tool_name=data.get("tool_name", ""),
                target_duration_minutes=int(data.get("target_duration_minutes", 10)),
                word_count=int(data.get("word_count", 0)),
                sections=sections,
                full_text=data.get("full_text", "")
            )

    @dataclass
    class AudioAsset(CompatibleBase):
        section_id: int
        file_path: str
        duration_sec: float

        @classmethod
        def model_validate(cls, data: Dict[str, Any]):
            return cls(
                section_id=data.get("section_id", 0),
                file_path=data.get("file_path", ""),
                duration_sec=float(data.get("duration_sec", 0.0))
            )

    @dataclass
    class VisualAsset(CompatibleBase):
        scene_id: int
        file_path: str
        prompt: str
        duration_sec: float

        @classmethod
        def model_validate(cls, data: Dict[str, Any]):
            return cls(
                scene_id=data.get("scene_id", 0),
                file_path=data.get("file_path", ""),
                prompt=data.get("prompt", ""),
                duration_sec=float(data.get("duration_sec", 0.0))
            )

    @dataclass
    class ChapterMarker(CompatibleBase):
        title: str
        timestamp_seconds: float
        timestamp_formatted: str

        @classmethod
        def model_validate(cls, data: Dict[str, Any]):
            return cls(
                title=data.get("title", ""),
                timestamp_seconds=float(data.get("timestamp_seconds", 0.0)),
                timestamp_formatted=data.get("timestamp_formatted", "00:00")
            )

    @dataclass
    class VideoMetadata(CompatibleBase):
        title: str
        description: str
        tags: List[str] = field(default_factory=list)
        category_id: str = "28"
        privacy_status: str = "private"
        chapters: List[ChapterMarker] = field(default_factory=list)
        ai_disclosure: bool = True

        @classmethod
        def model_validate(cls, data: Dict[str, Any]):
            chapters = [ChapterMarker.model_validate(c) for c in data.get("chapters", [])]
            return cls(
                title=data.get("title", ""),
                description=data.get("description", ""),
                tags=data.get("tags", []),
                category_id=data.get("category_id", "28"),
                privacy_status=data.get("privacy_status", "private"),
                chapters=chapters,
                ai_disclosure=data.get("ai_disclosure", True)
            )

    @dataclass
    class ProjectState(CompatibleBase):
        project_id: str
        current_stage: int = 1
        status: str = "initialized"
        error_message: Optional[str] = None
        created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
        updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
        topic: Optional[Topic] = None
        script: Optional[VideoScript] = None
        audio_assets: List[AudioAsset] = field(default_factory=list)
        master_audio_path: Optional[str] = None
        visual_assets: List[VisualAsset] = field(default_factory=list)
        timeline_json_path: Optional[str] = None
        subtitles_path: Optional[str] = None
        final_video_path: Optional[str] = None
        thumbnail_path: Optional[str] = None
        metadata: Optional[VideoMetadata] = None
        youtube_video_id: Optional[str] = None
        youtube_video_url: Optional[str] = None

        def update_timestamp(self) -> None:
            self.updated_at = datetime.now(timezone.utc).isoformat()

        @classmethod
        def model_validate(cls, data: Dict[str, Any]):
            topic = Topic.model_validate(data["topic"]) if data.get("topic") else None
            script = VideoScript.model_validate(data["script"]) if data.get("script") else None
            audio_assets = [AudioAsset.model_validate(a) for a in data.get("audio_assets", [])]
            visual_assets = [VisualAsset.model_validate(v) for v in data.get("visual_assets", [])]
            metadata = VideoMetadata.model_validate(data["metadata"]) if data.get("metadata") else None
            return cls(
                project_id=data.get("project_id", ""),
                current_stage=data.get("current_stage", 1),
                status=data.get("status", "initialized"),
                error_message=data.get("error_message"),
                created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
                updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
                topic=topic,
                script=script,
                audio_assets=audio_assets,
                master_audio_path=data.get("master_audio_path"),
                visual_assets=visual_assets,
                timeline_json_path=data.get("timeline_json_path"),
                subtitles_path=data.get("subtitles_path"),
                final_video_path=data.get("final_video_path"),
                thumbnail_path=data.get("thumbnail_path"),
                metadata=metadata,
                youtube_video_id=data.get("youtube_video_id"),
                youtube_video_url=data.get("youtube_video_url")
            )
