import React from "react";
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { Toaster } from "react-hot-toast";
import { notFound } from 'next/navigation';
import { locales } from '../../i18n';

export default async function LocaleLayout({
  children,
  params
}: Readonly<{
  children: React.ReactNode;
  params: { locale: string };
}>) {
  // Await params as required in Next.js 15
  const { locale } = await params;
  
  // Validate the locale parameter
  if (!locales.includes(locale as any)) {
    notFound();
  }

  // Providing all messages to the client
  // side is the easiest way to get started
  const messages = await getMessages({ locale });

  return (
    <NextIntlClientProvider messages={messages}>
      <Toaster position="top-center" reverseOrder={false} />
      <main className="min-h-screen">{children}</main>
    </NextIntlClientProvider>
  );
}
