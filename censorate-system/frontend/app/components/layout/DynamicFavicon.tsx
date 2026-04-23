'use client';

import { useEffect, useRef } from 'react';
import { useProjectStore } from '@/app/stores/projectStore';

export default function DynamicFavicon() {
  const { currentProject } = useProjectStore();
  const linkRefs = useRef<HTMLLinkElement[]>([]);

  useEffect(() => {
    const emoji = currentProject?.settings?.emoji;

    try {
      // Clean up previous favicons we created
      linkRefs.current.forEach(link => {
        if (link && link.parentNode) {
          link.parentNode.removeChild(link);
        }
      });
      linkRefs.current = [];

      if (!emoji) {
        return;
      }

      // Create canvas to render emoji as favicon
      const canvas = document.createElement('canvas');
      canvas.width = 128;
      canvas.height = 128;
      const ctx = canvas.getContext('2d');

      if (ctx) {
        // Draw background
        ctx.fillStyle = '#f8fafc';
        ctx.fillRect(0, 0, 128, 128);

        // Draw rounded background for emoji
        ctx.beginPath();
        ctx.arc(64, 64, 52, 0, Math.PI * 2);
        ctx.fillStyle = '#e2e8f0';
        ctx.fill();

        // Draw emoji
        ctx.font = '80px Arial, Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(emoji, 64, 64);

        // Create favicon link
        const link = document.createElement('link');
        link.type = 'image/png';
        link.rel = 'icon';
        link.href = canvas.toDataURL();
        document.head.appendChild(link);
        linkRefs.current.push(link);

        // Also add shortcut icon for compatibility
        const shortcutLink = document.createElement('link');
        shortcutLink.type = 'image/png';
        shortcutLink.rel = 'shortcut icon';
        shortcutLink.href = canvas.toDataURL();
        document.head.appendChild(shortcutLink);
        linkRefs.current.push(shortcutLink);
      }
    } catch (error) {
      console.error('Error in DynamicFavicon:', error);
    }
  }, [currentProject?.settings?.emoji]);

  return null;
}
