"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { useAuth } from "@/lib/auth-context";
import { buttonClass } from "@/lib/ui";

const NAV_LINKS = [
  { href: "/learn", label: "Учить слова" },
  { href: "/quiz", label: "Квиз" },
  { href: "/grammar", label: "Грамматика" },
  { href: "/words", label: "Мои слова" },
];

export function Navbar() {
  const { user, loading, logout } = useAuth();
  const pathname = usePathname();

  const isImmersive = pathname.startsWith("/learn/");
  if (isImmersive) return null;

  return (
    <header className="sticky top-0 z-10 border-b border-zinc-200 bg-white/80 backdrop-blur-sm dark:border-zinc-800 dark:bg-black/80">
      <div className="mx-auto max-w-4xl px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-2">
          <Link
            href="/"
            className="flex shrink-0 items-center gap-1.5 text-lg font-semibold text-zinc-900 dark:text-zinc-50"
          >
            <span aria-hidden>🌍</span> Полиглот
          </Link>

          <div className="flex flex-wrap items-center justify-end gap-2 sm:gap-3">
            <LanguageSwitcher />

            {!loading && user && (
              <button onClick={logout} className={buttonClass("ghost", "!px-0")}>
                Выйти
              </button>
            )}

            {!loading && !user && (
              <div className="flex gap-2">
                <Link href="/login" className={buttonClass("secondary")}>
                  Войти
                </Link>
                <Link href="/register" className={buttonClass("primary")}>
                  Регистрация
                </Link>
              </div>
            )}
          </div>
        </div>

        {user && (
          <nav className="-mx-4 mt-2 flex gap-1 overflow-x-auto px-4 text-sm [scrollbar-width:none] sm:mx-0 sm:flex-wrap sm:overflow-visible sm:px-0 [&::-webkit-scrollbar]:hidden">
            {NAV_LINKS.map((link) => {
              const active = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`shrink-0 whitespace-nowrap rounded-lg px-2.5 py-1.5 font-medium transition-colors ${
                    active
                      ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400"
                      : "text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>
        )}
      </div>
    </header>
  );
}
