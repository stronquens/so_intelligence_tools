export type SessionMode = "translate_es_openai_realtime" | "translate_es_chunked";

export interface LanguageOption {
  code: string;
  label: string;
}

export type UiEvent =
  | { type: "session_state"; state: string; message: string }
  | { type: "partial"; kind: "original" | "translation"; text: string }
  | {
      type: "block";
      id: string;
      sourceText?: string;
      translatedText: string;
      timestamp: string;
      speakerLabel?: string;
    }
  | { type: "mode"; mode: SessionMode }
  | { type: "voice_translation_state"; active: boolean; message: string; state?: string }
  | { type: "voice_translation_output"; chunks: number; bytes: number }
  | { type: "audio_level"; source: "system" | "microphone"; level: number }
  | {
      type: "session_config";
      sourceLanguage: string;
      targetLanguage: string;
      languages: LanguageOption[];
    }
  | { type: "error"; message: string };

export type UiCommand =
  | { type: "pause" }
  | { type: "resume" }
  | { type: "reset" }
  | { type: "stop" }
  | { type: "toggle_voice_translation" }
  | { type: "change_mode"; mode: SessionMode }
  | {
      type: "change_languages";
      sourceLanguage: string;
      targetLanguage: string;
    };

export interface UiCommandResult {
  accepted: boolean;
  message?: string;
}

export interface TranslatorReadyResult {
  accepted: boolean;
  events: UiEvent[];
}

export type TranslatorWindowAction = "close" | "minimize" | "toggle-maximize";

export type OverlayToolId =
  | "selected-text-correction"
  | "screenshot-ocr"
  | "system-audio-translation"
  | "voice-translation-microphone"
  | "push-to-talk-dictation"
  | "assistant"
  | "summary"
  | "intelligent-capture";

export type ShortcutActionId = OverlayToolId | "open-overlay";

export interface ShortcutSetting {
  id: ShortcutActionId;
  label: string;
  value: string;
}

export interface DesktopSettings {
  shortcuts: ShortcutSetting[];
  startAtLogin: boolean;
  overlayAlwaysVisible: boolean;
}

export type DesktopCommand =
  | { type: "run-tool"; toolId: OverlayToolId }
  | { type: "open-translator" }
  | { type: "hide-overlay" }
  | { type: "toggle-settings" }
  | { type: "close-settings" }
  | { type: "get-settings" }
  | { type: "save-settings"; settings: DesktopSettings };

export type DesktopCommandStatus = "success" | "failed" | "pending";

export interface DesktopCommandResult {
  status: DesktopCommandStatus;
  message: string;
  toolId?: OverlayToolId;
  details?: string;
  settings?: DesktopSettings;
}

export interface TranscriptPair {
  id: string;
  timestamp: string;
  sourceText: string;
  translatedText: string;
  speakerLabel?: string;
  status: "complete" | "streaming";
}
