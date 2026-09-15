"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { buttonClass, cardClass } from "@/lib/ui";

const FEATURES = [
  {
    href: "/learn",
    icon: "🃏",
    title: "Учить слова",
    description: "Карточки со свайпами и интервальным повторением.",
  },
  {
    href: "/quiz",
    icon: "🎯",
    title: "Квиз",
    description: "Проверь себя: выбор перевода или на слух.",
  },
  {
    href: "/grammar",
    icon: "📘",
    title: "Грамматика",
    description: "Короткие правила для начинающих, по уровням.",
  },
  {
    href: "/words",
    icon: "✏️",
    title: "Мои слова",
    description: "Добавляй свои слова — они сразу попадут в обучение.",
  },
];

export default function Home() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <main className="flex flex-1 items-center justify-center">
        <p className="text-zinc-500">Загрузка...</p>
      </main>
    );
  }

  if (user) {
    return (
      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-6 px-4 py-10">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
            С возвращением, {user.first_name || user.email.split("@")[0]}! 👋
          </h1>
          <p className="mt-1 text-zinc-500">Чем займёмся сегодня?</p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {FEATURES.map((f) => (
            <Link
              key={f.href}
              href={f.href}
              className={`${cardClass} flex items-start gap-4 p-5 transition-transform hover:-translate-y-0.5 hover:shadow-md`}
            >
              <span className="text-3xl" aria-hidden>
                {f.icon}
              </span>
              <div>
                <p className="font-semibold text-zinc-900 dark:text-zinc-50">{f.title}</p>
                <p className="mt-1 text-sm text-zinc-500">{f.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </main>
    );
  }

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 px-4 py-16 text-center">
      <div className="flex flex-col items-center gap-3">
        <span className="text-5xl" aria-hidden>
          🌍
        </span>
        <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-50">Полиглот</h1>
        <p className="max-w-sm text-zinc-500">
          Учи английский и немецкий: слова свайпами, короткая грамматика и квизы —
          просто и без воды.
        </p>
      </div>

      <div className="flex gap-3">
        <Link href="/register" className={buttonClass("primary", "px-6 py-2.5")}>
          Начать бесплатно
        </Link>
        <Link href="/login" className={buttonClass("secondary", "px-6 py-2.5")}>
          Войти
        </Link>
      </div>

      <Link href="/grammar" className="text-sm text-zinc-500 underline underline-offset-2 hover:text-indigo-600">
        Посмотреть грамматику без регистрации
      </Link>
    </main>
  );
}
