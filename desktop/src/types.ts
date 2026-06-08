export type SessionMode = "translate_es_openai_realtime" | "translate_es_chunked";

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
  | { type: "error"; message: string };

export type UiCommand =
  | { type: "pause" }
  | { type: "resume" }
  | { type: "reset" }
  | { type: "stop" }
  | { type: "change_mode"; mode: SessionMode };

export interface TranscriptPair {
  id: string;
  timestamp: string;
  sourceText: string;
  translatedText: string;
  speakerLabel?: string;
  status: "complete" | "streaming";
}
