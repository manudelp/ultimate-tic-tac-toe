import Link from "next/link";
import { FileText, Gamepad2, Code2, UserCheck, AlertTriangle, Scale, RefreshCw, Mail } from "lucide-react";
import SectionNav from "@/components/ui/section-nav";

const SECTIONS = [
  { id: "acceptance", title: "Acceptance",    icon: "FileText" },
  { id: "use",        title: "Use of the Game", icon: "Gamepad2" },
  { id: "ip",         title: "IP",             icon: "Code2" },
  { id: "conduct",    title: "User Conduct",   icon: "UserCheck" },
  { id: "disclaimer", title: "Disclaimer",     icon: "AlertTriangle" },
  { id: "liability",  title: "Liability",      icon: "Scale" },
  { id: "changes",    title: "Changes",        icon: "RefreshCw" },
  { id: "contact",    title: "Contact",        icon: "Mail" },
];

export default function TermsOfService() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-8 pt-4 pb-12 sm:py-12">

      {/* Header */}
      <div className="mb-12">
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">Legal</p>
        <h1 className="text-4xl font-bold mb-3">Terms of Service</h1>
        <p className="text-muted-foreground text-base leading-relaxed max-w-xl">
          Last updated: April 2026
        </p>
      </div>

      <div className="flex flex-col md:flex-row md:gap-12">

        <SectionNav sections={SECTIONS} />

        {/* Content */}
        <div className="flex-1 min-w-0 space-y-16">

          <section id="acceptance" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                <FileText className="w-4 h-4 text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold">Acceptance</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              By accessing or playing Ultimate Tic Tac Toe, you agree to these Terms of Service. If you do not agree, please do not use the game. No account or registration is required to play.
            </p>
          </section>

          <section id="use" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center shrink-0">
                <Gamepad2 className="w-4 h-4 text-purple-400" />
              </div>
              <h2 className="text-2xl font-bold">Use of the Game</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed mb-4">
              Ultimate Tic Tac Toe is a free, browser-based strategy game. You may use it for personal, non-commercial purposes. You agree not to:
            </p>
            <ul className="space-y-2">
              {[
                "Attempt to disrupt, overload, or exploit the game servers.",
                "Use automated scripts or bots to interact with the game outside of normal gameplay.",
                "Reverse-engineer or scrape the game in ways that harm its availability for other players.",
              ].map((item) => (
                <li key={item} className="flex gap-3 text-sm text-muted-foreground leading-relaxed">
                  <span className="text-purple-400 mt-0.5 shrink-0">→</span>
                  {item}
                </li>
              ))}
            </ul>
          </section>

          <section id="ip" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-yellow-500/10 flex items-center justify-center shrink-0">
                <Code2 className="w-4 h-4 text-yellow-400" />
              </div>
              <h2 className="text-2xl font-bold">Intellectual Property</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              The source code for this project is available under the MIT License. You are free to fork, modify, and redistribute it under the terms of that license. The game name, logo, and visual design remain the property of the author.
            </p>
          </section>

          <section id="conduct" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center shrink-0">
                <UserCheck className="w-4 h-4 text-green-400" />
              </div>
              <h2 className="text-2xl font-bold">User Conduct</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              This is an anonymous game — there are no user accounts, chat, or user-generated content. The only interaction is gameplay moves sent over a WebSocket connection. Play fairly and enjoy the game.
            </p>
          </section>

          <section id="disclaimer" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center shrink-0">
                <AlertTriangle className="w-4 h-4 text-orange-400" />
              </div>
              <h2 className="text-2xl font-bold">Disclaimer</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              The game is provided &quot;as is&quot; without warranties of any kind. We do not guarantee uninterrupted availability — the backend runs on a free-tier server and may occasionally be slow to start or temporarily unavailable. We are not responsible for lost game sessions due to server restarts or network issues.
            </p>
          </section>

          <section id="liability" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center shrink-0">
                <Scale className="w-4 h-4 text-red-400" />
              </div>
              <h2 className="text-2xl font-bold">Limitation of Liability</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              To the fullest extent permitted by law, the author shall not be liable for any indirect, incidental, or consequential damages arising from your use of the game. Since the game is free and collects no personal data, your exposure is limited to the time spent playing.
            </p>
          </section>

          <section id="changes" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                <RefreshCw className="w-4 h-4 text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold">Changes</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              These terms may be updated as the game evolves. The &quot;Last updated&quot; date at the top of this page will reflect any changes. Continued use of the game after an update constitutes acceptance of the revised terms.
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
              Questions about these terms? Reach out via <a href="https://www.linkedin.com/in/manuel-delpino/" target="_blank" rel="noopener noreferrer" className="text-foreground underline underline-offset-4 hover:text-muted-foreground transition-colors">Manuel Delpino</a> or <a href="https://www.linkedin.com/in/manuel-meiri%C3%B1o-7b9214331/" target="_blank" rel="noopener noreferrer" className="text-foreground underline underline-offset-4 hover:text-muted-foreground transition-colors">Manuel Meiriño</a> on LinkedIn.
            </p>
          </section>

          <div className="pt-4 border-t border-border/50 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground">Read our privacy policy too.</p>
            <Link
              href="/privacy-policy"
              className="inline-flex items-center gap-2 px-6 py-2.5 border border-border/50 hover:border-border text-sm font-semibold rounded-lg transition-colors"
            >
              Privacy Policy →
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}
