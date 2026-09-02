import api from './client';
import { Conversation, ChatMessage } from '../types/chat';

export const getConversations = async (): Promise<Conversation[]> => {
  const res = await api.get('/conversations');
  return res.data;
};

export const createConversation = async (): Promise<Conversation> => {
  const res = await api.post('/conversations');
  return res.data;
};

export const getConversationMessages = async (id: number): Promise<ChatMessage[]> => {
  const res = await api.get(`/conversations/${id}/messages`);
  return res.data;
};

export const deleteConversation = async (id: number) => {
  const res = await api.delete(`/conversations/${id}`);
  return res.data;
};

export interface FeedbackPayload {
  conversationId: number;
  messageId: number;
  parentUserMessageId?: number;
  rating: 'up' | 'down';
  reasonCode?: string;
  comment?: string;
  prompt?: string;
  responseContent?: string;
  locale?: string;
}

export const submitMessageFeedback = async (payload: FeedbackPayload) => {
  const res = await api.post('/chat/feedback', payload);
  return res.data;
};

export const updateMessageFeedback = async (feedbackId: number, payload: Partial<FeedbackPayload>) => {
  const res = await api.patch(`/chat/feedback/${feedbackId}`, payload);
  return res.data;
};

export const deleteMessageFeedback = async (feedbackId: number) => {
  const res = await api.delete(`/chat/feedback/${feedbackId}`);
  return res.data;
};

