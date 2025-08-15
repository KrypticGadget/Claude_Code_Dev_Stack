/**
 * Chat message model
 * Ported from Flutter ChatMessage model (@9cat) - MIT License
 */

export enum MessageType {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system',
  ERROR = 'error'
}

export interface ChatMessage {
  id: string;
  content: string;
  type: MessageType;
  timestamp: Date;
  isLoading?: boolean;
}

export class ChatMessageImpl implements ChatMessage {
  id: string;
  content: string;
  type: MessageType;
  timestamp: Date;
  isLoading: boolean;

  constructor(config: {
    id: string;
    content: string;
    type: MessageType;
    timestamp: Date;
    isLoading?: boolean;
  }) {
    this.id = config.id;
    this.content = config.content;
    this.type = config.type;
    this.timestamp = config.timestamp;
    this.isLoading = config.isLoading || false;
  }

  copyWith(updates: Partial<ChatMessage>): ChatMessageImpl {
    return new ChatMessageImpl({
      id: updates.id ?? this.id,
      content: updates.content ?? this.content,
      type: updates.type ?? this.type,
      timestamp: updates.timestamp ?? this.timestamp,
      isLoading: updates.isLoading ?? this.isLoading,
    });
  }

  toJson(): Record<string, any> {
    return {
      id: this.id,
      content: this.content,
      type: this.type,
      timestamp: this.timestamp.toISOString(),
      isLoading: this.isLoading,
    };
  }

  static fromJson(json: Record<string, any>): ChatMessageImpl {
    return new ChatMessageImpl({
      id: json.id,
      content: json.content,
      type: Object.values(MessageType).find(type => type === json.type) || MessageType.USER,
      timestamp: new Date(json.timestamp),
      isLoading: json.isLoading || false,
    });
  }
}