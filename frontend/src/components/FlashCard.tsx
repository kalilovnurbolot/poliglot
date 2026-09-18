"use client";

import { motion, useAnimation, type PanInfo } from "framer-motion";
import { forwardRef, useImperativeHandle, useState } from "react";
import type { ReviewCard, SwipeDirection } from "@/lib/review";

export type FlashCardHandle = {
  swipe: (direction: SwipeDirection) => void;
};

const EXIT_DISTANCE = 600;
const SWIPE_THRESHOLD = 100;

const EXIT_OFFSET: Record<SwipeDirection, { x: number; y: number; rotate: number }> = {
  right: { x: EXIT_DISTANCE, y: 0, rotate: 20 },
  left: { x: -EXIT_DISTANCE, y: 0, rotate: -20 },
  up: { x: 0, y: -EXIT_DISTANCE, rotate: 0 },
  down: { x: 0, y: EXIT_DISTANCE, rotate: 0 },
};

const DIRECTION_LABEL: Record<SwipeDirection, string> = {
  right: "Знаю",
  left: "Не знаю",
  up: "В избранное",
  down: "Пропустить",
};

const DIRECTION_COLOR: Record<SwipeDirection, string> = {
  right: "bg-emerald-600",
  left: "bg-red-600",
  up: "bg-amber-500",
  down: "bg-zinc-600",
};

type Props = {
  card: ReviewCard;
  onSwipe: (direction: SwipeDirection) => void;
};

export const FlashCard = forwardRef<FlashCardHandle, Props>(function FlashCard(
  { card, onSwipe },
  ref,
) {
  const controls = useAnimation();
  const [flipped, setFlipped] = useState(false);
  const [hint, setHint] = useState<SwipeDirection | null>(null);

  const triggerSwipe = async (direction: SwipeDirection) => {
    setHint(direction);
    await controls.start({
      ...EXIT_OFFSET[direction],
      opacity: 0,
      transition: { duration: 0.25, ease: "easeIn" },
    });
    onSwipe(direction);
  };

  useImperativeHandle(ref, () => ({ swipe: triggerSwipe }));

  const handleDragEnd = (_: unknown, info: PanInfo) => {
    const { offset } = info;
    if (Math.abs(offset.x) > Math.abs(offset.y)) {
      if (offset.x > SWIPE_THRESHOLD) return triggerSwipe("right");
      if (offset.x < -SWIPE_THRESHOLD) return triggerSwipe("left");
    } else {
      if (offset.y < -SWIPE_THRESHOLD) return triggerSwipe("up");
      if (offset.y > SWIPE_THRESHOLD) return triggerSwipe("down");
    }
    controls.start({ x: 0, y: 0, rotate: 0, transition: { type: "spring", stiffness: 300, damping: 20 } });
    setHint(null);
  };

  const textLength = card.word.text.length;
  const textSizeClass = textLength > 40 ? "text-lg" : textLength > 20 ? "text-2xl" : "text-3xl";

  return (
    <div className="relative flex h-96 w-full max-w-sm items-center justify-center sm:h-[26rem] sm:w-80">
      <div className="pointer-events-none absolute inset-x-0 -top-6 flex justify-center gap-6 text-xs text-zinc-400">
        <span>← не знаю</span>
        <span>знаю →</span>
      </div>

      <motion.div
        drag
        dragElastic={0.6}
        dragConstraints={{ top: 0, bottom: 0, left: 0, right: 0 }}
        onDragEnd={handleDragEnd}
        onDrag={(_, info) => {
          const { offset } = info;
          if (Math.abs(offset.x) < 20 && Math.abs(offset.y) < 20) {
            setHint(null);
            return;
          }
          if (Math.abs(offset.x) > Math.abs(offset.y)) {
            setHint(offset.x > 0 ? "right" : "left");
          } else {
            setHint(offset.y > 0 ? "down" : "up");
          }
        }}
        animate={controls}
        whileTap={{ cursor: "grabbing" }}
        onClick={() => setFlipped((f) => !f)}
        className="flex h-full w-full cursor-grab flex-col items-center justify-center gap-3 rounded-2xl border border-zinc-200 bg-white p-6 text-center shadow-lg select-none dark:border-zinc-800 dark:bg-zinc-900"
      >
        {hint && (
          <span
            className={`absolute top-3 rounded-full px-3 py-1 text-xs font-medium text-white ${DIRECTION_COLOR[hint]}`}
          >
            {DIRECTION_LABEL[hint]}
          </span>
        )}

        <div className="absolute top-3 right-3 rounded-full border border-zinc-200 px-2 py-0.5 text-xs text-zinc-400 dark:border-zinc-700">
          {card.word.level}
        </div>

        {!flipped ? (
          <>
            <p className={`${textSizeClass} break-words font-semibold leading-snug text-zinc-900 dark:text-zinc-50`}>
              {card.word.text}
            </p>
            {card.word.transcription && (
              <p className="text-zinc-500">{card.word.transcription}</p>
            )}
            <p className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400">
              {card.word.part_of_speech}
            </p>
            <p className="mt-4 text-xs text-zinc-400">нажмите, чтобы увидеть перевод</p>
          </>
        ) : (
          <>
            <p
              className={`${card.word.translation.length > 30 ? "text-lg" : "text-2xl"} break-words font-semibold leading-snug text-zinc-900 dark:text-zinc-50`}
            >
              {card.word.translation}
            </p>
            {card.word.example_sentence && (
              <p className="text-sm text-zinc-500 italic">&laquo;{card.word.example_sentence}&raquo;</p>
            )}
          </>
        )}
      </motion.div>

      <div className="pointer-events-none absolute inset-x-0 -bottom-6 flex justify-center text-xs text-zinc-400">
        ↑ избранное · ↓ пропустить
      </div>
    </div>
  );
});
