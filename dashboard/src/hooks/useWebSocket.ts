import { useEffect, useState, useRef, useCallback } from 'react';
import { WebSocketEnvelope } from '../types';

type MessageHandler = (envelope: WebSocketEnvelope) => void;

interface UseWebSocketReturn {
  isConnected: boolean;
  lastMessage: WebSocketEnvelope | null;
  subscribe: (eventType: string, handler: MessageHandler) => () => void;
  sendPing: () => void;
}

export function useWebSocket(): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastMessage, setLastMessage] = useState<WebSocketEnvelope | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const listenersRef = useRef<Map<string, Set<MessageHandler>>>(new Map());

  const getWsUrl = (): string => {
    if (import.meta.env.VITE_WS_URL) {
      return import.meta.env.VITE_WS_URL;
    }
    const loc = window.location;
    const protocol = loc.protocol === 'https:' ? 'wss:' : 'ws:';
    return protocol + '//localhost:8000/ws/live';
  };

  const connect = useCallback(() => {
    if (socketRef.current && (socketRef.current.readyState === WebSocket.OPEN || socketRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      const url = getWsUrl();
      const ws = new WebSocket(url);
      socketRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        if (reconnectTimeoutRef.current) {
          window.clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      ws.onmessage = (event: MessageEvent) => {
        try {
          if (event.data === 'pong') return;
          const envelope: WebSocketEnvelope = JSON.parse(event.data);
          setLastMessage(envelope);

          // Dispatch to specific event listeners
          const eventListeners = listenersRef.current.get(envelope.event_type);
          if (eventListeners) {
            eventListeners.forEach((handler) => handler(envelope));
          }

          // Dispatch to wildcard listeners
          const wildcardListeners = listenersRef.current.get('*');
          if (wildcardListeners) {
            wildcardListeners.forEach((handler) => handler(envelope));
          }
        } catch {
          // ignore non-JSON or heartbeat responses
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        socketRef.current = null;
        // Exponential/Fixed auto-reconnect attempt
        if (!reconnectTimeoutRef.current) {
          reconnectTimeoutRef.current = window.setTimeout(() => {
            reconnectTimeoutRef.current = null;
            connect();
          }, 3000);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      setIsConnected(false);
      if (!reconnectTimeoutRef.current) {
        reconnectTimeoutRef.current = window.setTimeout(() => {
          reconnectTimeoutRef.current = null;
          connect();
        }, 3000);
      }
    }
  }, []);

  useEffect(() => {
    connect();

    // Heartbeat ping interval
    const pingInterval = window.setInterval(() => {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send('ping');
      }
    }, 15000);

    return () => {
      window.clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) {
        window.clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [connect]);

  const subscribe = useCallback((eventType: string, handler: MessageHandler) => {
    if (!listenersRef.current.has(eventType)) {
      listenersRef.current.set(eventType, new Set());
    }
    listenersRef.current.get(eventType)!.add(handler);

    return () => {
      const handlers = listenersRef.current.get(eventType);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          listenersRef.current.delete(eventType);
        }
      }
    };
  }, []);

  const sendPing = useCallback(() => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send('ping');
    }
  }, []);

  return {
    isConnected,
    lastMessage,
    subscribe,
    sendPing,
  };
}
