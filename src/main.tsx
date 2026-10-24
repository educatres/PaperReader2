import { createRoot } from 'react-dom/client';
import { registerSW } from 'virtual:pwa-register';
import App from './App';
import './styles.css';

// Apply the saved appearance before React paints to avoid a light-theme flash.
try {
  const saved = JSON.parse(localStorage.getItem('PaperReader.preferences') || '{}');
  const theme = saved.theme === 'dark' ? 'dark' : 'light';
  document.documentElement.dataset.theme = theme;
  document.documentElement.style.colorScheme = theme;
} catch { document.documentElement.dataset.theme = 'light'; }

// Do not reload an active research session automatically when a new release arrives.
registerSW({ immediate: true });
createRoot(document.getElementById('root')!).render(<App />);
