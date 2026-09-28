/**
 * Telegram Mini App (TMA) SDK Bridge
 * Gracefully integrates Telegram WebApp features with desktop/browser fallbacks
 */

interface TelegramWebApp {
  ready: () => void;
  expand: () => void;
  close: () => void;
  setHeaderColor: (color: string) => void;
  setBackgroundColor: (color: string) => void;
  enableClosingConfirmation: () => void;
  HapticFeedback?: {
    impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
    notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
    selectionChanged: () => void;
  };
  openTelegramLink: (url: string) => void;
  initDataUnsafe?: {
    user?: {
      first_name?: string;
      username?: string;
    };
  };
}

declare global {
  interface Window {
    Telegram?: {
      WebApp?: TelegramWebApp;
    };
  }
}

export class TmaBridge {
  private static instance: TmaBridge;
  private webApp: TelegramWebApp | null = null;

  private constructor() {
    if (typeof window !== 'undefined' && window.Telegram && window.Telegram.WebApp) {
      this.webApp = window.Telegram.WebApp;
      try {
        this.webApp.ready();
        this.webApp.expand();
        this.webApp.setHeaderColor('#070c14');
        this.webApp.setBackgroundColor('#070c14');
        this.webApp.enableClosingConfirmation();
      } catch (e) {
        console.warn('TMA initialization issue:', e);
      }
    }
  }

  public static getInstance(): TmaBridge {
    if (!TmaBridge.instance) {
      TmaBridge.instance = new TmaBridge();
    }
    return TmaBridge.instance;
  }

  public getPlayerName(): string {
    if (this.webApp?.initDataUnsafe?.user?.first_name) {
      return this.webApp.initDataUnsafe.user.first_name;
    }
    return 'Dervish';
  }

  public triggerHaptic(style: 'light' | 'medium' | 'heavy') {
    try {
      this.webApp?.HapticFeedback?.impactOccurred(style);
    } catch {
      // Ignore if not in Telegram
    }
  }

  public triggerHapticNotification(type: 'error' | 'success' | 'warning') {
    try {
      this.webApp?.HapticFeedback?.notificationOccurred(type);
    } catch {
      // Ignore
    }
  }

  public shareScore(score: number, characterName: string, survivalTime: string) {
    const text = `🌲 I scored ${score} chops with ${characterName} in Khanqah Rush! Survived for ${survivalTime}. Can you beat my score? ⚔️`;
    const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(window.location.href)}&text=${encodeURIComponent(text)}`;

    if (this.webApp?.openTelegramLink) {
      this.webApp.openTelegramLink(shareUrl);
    } else {
      window.open(shareUrl, '_blank');
    }
  }
}
