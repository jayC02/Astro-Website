import { useEffect } from 'react';
import Lenis from '@studio-freight/lenis';

export default function LenisWrapper() {
  useEffect(() => {
    const lenis = new Lenis();

    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }

    requestAnimationFrame(raf);
  }, []);

  return null;
}
