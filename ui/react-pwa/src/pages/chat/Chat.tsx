import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  Tooltip,
  Fab,
  Collapse,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Send as SendIcon,
  Mic as MicIcon,
  MicOff as MicOffIcon,
  Clear as ClearIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { Helmet } from 'react-helmet-async';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { useAppStore } from '../../store/appStore';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system' | 'error';
  content: string;
  timestamp: Date;
  metadata?: {
    model?: string;
    tokens?: number;
    cost?: number;
    duration?: number;
  };
}

const Chat: React.FC = () => {
  const {
    messages,
    isConnected,
    isTyping,
    currentInput,
    sendMessage,
    setCurrentInput,
    clearMessages,
    addNotification,
  } = useAppStore();

  const [isListening, setIsListening] = useState(false);
  const [showMetadata, setShowMetadata] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!currentInput.trim() || !isConnected) return;

    try {
      await sendMessage(currentInput);
      inputRef.current?.focus();
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Failed to send message',
        message: error instanceof Error ? error.message : 'Unknown error',
        read: false,
      });
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const handleVoiceToggle = () => {
    if (!isConnected) {
      addNotification({
        type: 'warning',
        title: 'Not connected',
        message: 'Please connect to the server first',
        read: false,
      });
      return;
    }

    setIsListening(!isListening);
    // Voice recognition implementation would go here
  };

  const handleClear = () => {
    clearMessages();
    addNotification({
      type: 'info',
      title: 'Chat cleared',
      message: 'All messages have been cleared',
      read: false,
    });
  };

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'user':
        return <PersonIcon />;
      case 'assistant':
        return <BotIcon />;
      case 'system':
        return <WarningIcon />;
      case 'error':
        return <ErrorIcon />;
      default:
        return <BotIcon />;
    }
  };

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'user':
        return 'primary';
      case 'assistant':
        return 'secondary';
      case 'system':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const renderMessageContent = (content: string) => {
    // Simple code block detection
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        parts.push(
          <Typography key={`text-${lastIndex}`} component="span" variant="body2">
            {content.slice(lastIndex, match.index)}
          </Typography>
        );
      }

      // Add code block
      const language = match[1] || 'text';
      const code = match[2];
      parts.push(
        <Box key={`code-${match.index}`} sx={{ my: 1 }}>
          <SyntaxHighlighter
            language={language}
            style={vscDarkPlus}
            customStyle={{
              borderRadius: 4,
              fontSize: '0.875rem',
            }}
          >
            {code}
          </SyntaxHighlighter>
        </Box>
      );

      lastIndex = codeBlockRegex.lastIndex;
    }

    // Add remaining text
    if (lastIndex < content.length) {
      parts.push(
        <Typography key={`text-${lastIndex}`} component="span" variant="body2">
          {content.slice(lastIndex)}
        </Typography>
      );
    }

    return parts.length > 0 ? parts : (
      <Typography variant="body2">{content}</Typography>
    );
  };

  const MessageBubble: React.FC<{ message: Message; index: number }> = ({ message, index }) => (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        delay: index * 0.1,
        type: "spring",
        stiffness: 500,
        damping: 30
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: 2,
          mb: 2,
          flexDirection: message.type === 'user' ? 'row-reverse' : 'row',
        }}
      >
        <Avatar
          sx={{
            bgcolor: `${getMessageColor(message.type)}.main`,
            width: 32,
            height: 32,
          }}
        >
          {getMessageIcon(message.type)}
        </Avatar>

        <Paper
          elevation={1}
          sx={{
            flex: 1,
            maxWidth: '70%',
            p: 2,
            bgcolor: message.type === 'user' 
              ? 'primary.main' 
              : message.type === 'error'
              ? 'error.dark'
              : 'background.paper',
            color: message.type === 'user' ? 'primary.contrastText' : 'text.primary',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Chip
              size="small"
              label={message.type}
              color={getMessageColor(message.type) as any}
              variant="outlined"
            />
            <Typography variant="caption" color="text.secondary">
              {formatTime(message.timestamp)}
            </Typography>
          </Box>

          <Box sx={{ mb: message.metadata ? 1 : 0 }}>
            {renderMessageContent(message.content)}
          </Box>

          {message.metadata && (
            <>
              <Tooltip title={showMetadata ? "Hide metadata" : "Show metadata"}>
                <IconButton
                  size="small"
                  onClick={() => setShowMetadata(!showMetadata)}
                  sx={{ mt: 1 }}
                >
                  {showMetadata ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Tooltip>
              
              <Collapse in={showMetadata}>
                <Box sx={{ mt: 1, pt: 1, borderTop: 1, borderColor: 'divider' }}>
                  <Typography variant="caption" color="text.secondary">
                    Model: {message.metadata.model || 'N/A'} | 
                    Tokens: {message.metadata.tokens || 'N/A'} | 
                    Duration: {message.metadata.duration || 'N/A'}ms
                  </Typography>
                </Box>
              </Collapse>
            </>
          )}
        </Paper>
      </Box>
    </motion.div>
  );

  return (
    <>
      <Helmet>
        <title>AI Chat - Claude Code Dev Stack</title>
        <meta name="description" content="Chat with Claude AI assistant for code generation and development help" />
      </Helmet>

      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Paper elevation={1} sx={{ p: 2, mb: 2, mx: 3, mt: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box>
              <Typography variant="h6" fontWeight={600}>
                Claude Code Assistant
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {isConnected ? 'Ready to help with your development tasks' : 'Not connected to server'}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Voice input">
                <IconButton
                  onClick={handleVoiceToggle}
                  color={isListening ? 'error' : 'default'}
                  disabled={!isConnected}
                >
                  {isListening ? <MicIcon /> : <MicOffIcon />}
                </IconButton>
              </Tooltip>
              
              <Tooltip title="Clear chat">
                <IconButton onClick={handleClear} disabled={messages.length === 0}>
                  <ClearIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Paper>

        {/* Connection warning */}
        {!isConnected && (
          <Box sx={{ mx: 3, mb: 2 }}>
            <Alert severity="warning" variant="outlined">
              Not connected to Claude Code server. Please check your connection settings.
            </Alert>
          </Box>
        )}

        {/* Messages area */}
        <Box sx={{ flex: 1, overflow: 'auto', px: 3 }}>
          {messages.length === 0 ? (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                textAlign: 'center',
              }}
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
              >
                <Avatar sx={{ width: 64, height: 64, mb: 2, bgcolor: 'primary.main' }}>
                  <BotIcon sx={{ fontSize: 32 }} />
                </Avatar>
                <Typography variant="h6" gutterBottom>
                  Welcome to Claude Code Chat
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 400 }}>
                  I'm here to help you with code generation, debugging, documentation, and any development questions you might have.
                  Start a conversation by typing a message below.
                </Typography>
              </motion.div>
            </Box>
          ) : (
            <AnimatePresence>
              {messages.map((message, index) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  index={index}
                />
              ))}
            </AnimatePresence>
          )}

          {/* Typing indicator */}
          <AnimatePresence>
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
                    <BotIcon />
                  </Avatar>
                  <Paper elevation={1} sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CircularProgress size={16} />
                      <Typography variant="body2" color="text.secondary">
                        Claude is typing...
                      </Typography>
                    </Box>
                  </Paper>
                </Box>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={messagesEndRef} />
        </Box>

        {/* Input area */}
        <Paper elevation={3} sx={{ m: 3, p: 2 }}>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
            <TextField
              ref={inputRef}
              fullWidth
              multiline
              maxRows={4}
              placeholder={isConnected ? "Type your message..." : "Connect to server to start chatting"}
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={!isConnected}
              variant="outlined"
              size="small"
            />
            
            <Tooltip title="Send message">
              <span>
                <IconButton
                  onClick={handleSend}
                  disabled={!isConnected || !currentInput.trim()}
                  color="primary"
                  sx={{
                    bgcolor: 'primary.main',
                    color: 'white',
                    '&:hover': {
                      bgcolor: 'primary.dark',
                    },
                    '&:disabled': {
                      bgcolor: 'action.disabledBackground',
                    },
                  }}
                >
                  <SendIcon />
                </IconButton>
              </span>
            </Tooltip>
          </Box>
        </Paper>

        {/* Voice recording indicator */}
        <AnimatePresence>
          {isListening && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              <Fab
                color="error"
                sx={{
                  position: 'fixed',
                  bottom: 100,
                  right: 24,
                }}
                onClick={handleVoiceToggle}
              >
                <MicIcon />
              </Fab>
            </motion.div>
          )}
        </AnimatePresence>
      </Box>
    </>
  );
};

export default Chat;