# Overview

This is a Discord self-bot (user bot) application built with Python and discord.py named "LevelX". The bot provides automated messaging features including auto-reply functionality, AFK status management, copycat capabilities, and voice channel management. Key features include the "lx!puxar" command for moving users by role to voice channels, "lx!mover" for moving users by role to specific voice channels without being in one, "lx!marcar" for mass mentioning users by role, and permission management with "lx!addperm" and "lx!removerperm" commands. All bot messages include "Developer by Tio Sunn'212" branding. It's designed to run as a personal Discord automation tool with customizable behaviors configured through JSON settings.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Application Structure
- **Entry Point**: `main.py` serves as the primary application file containing bot initialization and configuration loading
- **Configuration Management**: JSON-based configuration system using `config/config.json` for persistent settings
- **Command System**: Built on discord.py's commands extension with custom prefix support

## Bot Architecture
- **Self-Bot Implementation**: Uses discord.py-self library to run as a user account rather than a bot account
- **Modular Features**: Supports multiple automation features including auto-reply, AFK status, and user copying
- **Event-Driven Design**: Leverages Discord's event system for real-time message processing

## Configuration System
- **JSON Configuration**: Centralized settings management through `config/config.json`
- **Dynamic Updates**: Configuration can be modified and saved during runtime
- **Feature Toggles**: Individual features can be enabled/disabled through configuration

## Message Processing
- **Auto-Reply System**: Configurable automatic responses to messages in specified channels or from specific users
- **AFK Management**: Automatic status responses when marked as away from keyboard
- **Copycat Functionality**: Ability to mirror messages from specified users

## Audio and Media Features
- **Text-to-Speech**: Integration with Google Text-to-Speech (gTTS) for voice message generation
- **QR Code Generation**: Built-in QR code creation capabilities
- **ASCII Art**: Text formatting using pyfiglet for stylized output

# External Dependencies

## Core Libraries
- **discord.py-self**: Modified Discord library for self-bot functionality
- **requests**: HTTP client for API interactions
- **asyncio**: Asynchronous programming support for Discord events

## Utility Libraries
- **colorama**: Terminal color formatting for enhanced console output
- **gtts**: Google Text-to-Speech API integration
- **qrcode**: QR code generation and image processing
- **pyfiglet**: ASCII art text generation

## System Dependencies
- **Python 3.x**: Runtime environment
- **JSON**: Configuration file format
- **OS/Platform modules**: Cross-platform compatibility support

## Discord Integration
- **Discord API**: Primary service for bot functionality
- **User Authentication**: Token-based authentication system (via DISCORD_TOKEN environment variable)
- **Real-time Events**: WebSocket connection for live message processing

# Recent Changes

## Authorization System Fixes (2025-09-13)
- **Fixed addperm command**: Now works for all authorized users, not just the bot owner
- **Normalized ID types**: All user IDs are consistently stored as integers to prevent comparison failures
- **Unified authorization lists**: remoteuser command now adds users directly to authorized-users list
- **Enhanced command processing**: Added manual command processing for authorized non-owner users
- **Fixed message deletion**: Replaced direct ctx.message.delete() with safe_delete_message() to prevent permission errors

## New Voice Channel Features (2025-09-13)
- **Added lx!mover command**: New voice channel management command that moves users by role to specific channels
- **Enhanced voice management**: Users can now move role members to any voice channel using ID parameters without being in voice
- **Improved command syntax**: lx!mover <role_id> <channel_id> provides more flexible voice channel control

## GitHub Integration Note
User prefers manual GitHub integration over Replit's automatic integration system. Project files can be downloaded as zip for manual upload to GitHub repositories.