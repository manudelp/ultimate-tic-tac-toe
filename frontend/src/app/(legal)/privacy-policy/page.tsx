import Link from "next/link";
import { Shield, Database, Share2, Lock, Baby, RefreshCw, Mail } from "lucide-react";
import SectionNav from "@/components/ui/section-nav";

const SECTIONS = [
  { id: "collection", title: "What We Collect", icon: "Database" },
  { id: "use",        title: "How We Use It",   icon: "Shield" },
  { id: "sharing",    title: "Sharing",          icon: "Share2" },
  { id: "security",   title: "Security",         icon: "Lock" },
  { id: "children",   title: "Children",         icon: "Baby" },
  { id: "changes",    title: "Changes",          icon: "RefreshCw" },
  { id: "contact",    title: "Contact",          icon: "Mail" },
];

export default function PrivacyPolicy() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-8 pt-4 pb-12 sm:py-12">

      {/* Header */}
      <div className="mb-12">
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">Legal</p>
        <h1 className="text-4xl font-bold mb-3">Privacy Policy</h1>
        <p className="text-muted-foreground text-base leading-relaxed max-w-xl">
          Last updated: April 2026
        </p>
      </div>

      <div className="flex flex-col md:flex-row md:gap-12">

        <SectionNav sections={SECTIONS} />

        {/* Content */}
        <div className="flex-1 min-w-0 space-y-16">

          <section id="collection" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                <Database className="w-4 h-4 text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold">What We Collect</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed mb-4">
              Ultimate Tic Tac Toe does not require an account and does not collect any personally identifiable information. The only data processed is:
            </p>
            <div className="space-y-3">
              {[
                { title: "Anonymous usage analytics", desc: "Page views, performance metrics, and general usage patterns collected by Vercel Analytics and Vercel Speed Insights. This data is aggregated and cannot be used to identify you." },
                { title: "Game session data", desc: "Temporary in-memory game state (board positions, moves, clocks) held on our server for the duration of your session. This is never written to a database and is discarded when the session ends." },
                { title: "Session storage", desc: "Your browser's sessionStorage is used to resume an active game if you reload the page. This data never leaves your device and is cleared when you close the tab." },
              ].map(({ title, desc }) => (
                <div key={title} className="flex gap-4 p-4 rounded-xl border border-border/50 bg-background">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0 mt-2" />
                  <div>
                    <p className="text-sm font-semibold mb-1">{title}</p>
                    <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section id="use" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center shrink-0">
                <Shield className="w-4 h-4 text-purple-400" />
              </div>
              <h2 className="text-2xl font-bold">How We Use It</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed mb-4">
              The limited data we process is used solely to:
            </p>
            <ul className="space-y-2">
              {[
                "Run and maintain the game (matchmaking, real-time gameplay, bot moves).",
                "Monitor performance and fix bugs using aggregated analytics.",
                "Understand general usage trends to improve the experience.",
              ].map((item) => (
                <li key={item} className="flex gap-3 text-sm text-muted-foreground leading-relaxed">
                  <span className="text-purple-400 mt-0.5 shrink-0">→</span>
                  {item}
                </li>
              ))}
            </ul>
          </section>

          <section id="sharing" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-yellow-500/10 flex items-center justify-center shrink-0">
                <Share2 className="w-4 h-4 text-yellow-400" />
              </div>
              <h2 className="text-2xl font-bold">Sharing</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed mb-4">
              We do not sell, trade, or rent any user data. The only third parties involved are our infrastructure providers:
            </p>
            <div className="space-y-3">
              {[
                { title: "Vercel", desc: "Hosts the frontend and provides anonymous analytics and speed insights.", link: "https://vercel.com/legal/privacy-policy" },
                { title: "Render", desc: "Hosts the backend game server. No personal data is stored on Render.", link: "https://render.com/privacy" },
              ].map(({ title, desc, link }) => (
                <div key={title} className="flex gap-4 p-4 rounded-xl border border-border/50 bg-background">
                  <div className="w-1.5 h-1.5 rounded-full bg-yellow-400 shrink-0 mt-2" />
                  <div>
                    <a href={link} target="_blank" rel="noopener noreferrer" className="text-sm font-semibold underline underline-offset-4 hover:text-muted-foreground transition-colors">{title}</a>
                    <p className="text-sm text-muted-foreground leading-relaxed mt-1">{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section id="security" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center shrink-0">
                <Lock className="w-4 h-4 text-green-400" />
              </div>
              <h2 className="text-2xl font-bold">Security</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              All communication between your browser and our servers is encrypted via HTTPS and WSS. Since we do not store personal data, the risk surface is minimal. Game state is held in memory only and automatically discarded after your session ends.
            </p>
          </section>

          <section id="children" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-pink-500/10 flex items-center justify-center shrink-0">
                <Baby className="w-4 h-4 text-pink-400" />
              </div>
              <h2 className="text-2xl font-bold">Children</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              This game does not collect personal information from anyone, including children under 13. No account, email, or name is required to play.
            </p>
          </section>

          <section id="changes" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center shrink-0">
                <RefreshCw className="w-4 h-4 text-orange-400" />
              </div>
              <h2 className="text-2xl font-bold">Changes</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              If this policy changes materially, the &quot;Last updated&quot; date at the top of this page will be revised. Continued use of the game after changes constitutes acceptance of the updated policy.
            </p>
          </section>

          <section id="contact" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                <Mail className="w-4 h-4 text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold">Contact</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              Questions about this policy? Reach out via <a href="https://www.linkedin.com/in/manuel-delpino/" target="_blank" rel="noopener noreferrer" className="text-foreground underline underline-offset-4 hover:text-muted-foreground transition-colors">Manuel Delpino</a> or <a href="https://www.linkedin.com/in/manuel-meiri%C3%B1o-7b9214331/" target="_blank" rel="noopener noreferrer" className="text-foreground underline underline-offset-4 hover:text-muted-foreground transition-colors">Manuel Meiriño</a> on LinkedIn.
            </p>
          </section>

          <div className="pt-4 border-t border-border/50 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground">Read our terms of service too.</p>
            <Link
              href="/terms-of-service"
              className="inline-flex items-center gap-2 px-6 py-2.5 border border-border/50 hover:border-border text-sm font-semibold rounded-lg transition-colors"
            >
              Terms of Service →
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}
