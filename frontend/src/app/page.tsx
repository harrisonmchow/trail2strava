"use client";
import { AllTrailsToStravaLogo } from '@/components/Logo'
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Link2, FileUp, CheckCircle2 } from "lucide-react";
import { ConnectStravaButton } from "@/components/ConnectStravaButton";
import { Header } from "@/components/Header";
import { getAuthStatus } from "@/lib/api";

const steps = [
  {
    number: 1,
    icon: <Link2 className="w-6 h-6" />,
    title: "Connect Strava",
    description: "Authorize your Strava account securely",
  },
  {
    number: 2,
    icon: <FileUp className="w-6 h-6" />,
    title: "Upload GPX",
    description: "Download & upload your AllTrails GPX file",
  },
  {
    number: 3,
    icon: <CheckCircle2 className="w-6 h-6" />,
    title: "Sync Activity",
    description: "GPS data, splits & stats appear on Strava",
  },
];

function FloatingPaths({ position }: { position: number }) {
  const paths = Array.from({ length: 24 }, (_, i) => ({
    id: i,
    d: `M-${380 - i * 5 * position} -${189 + i * 6}C-${380 - i * 5 * position} -${189 + i * 6} -${312 - i * 5 * position} ${216 - i * 6} ${152 - i * 5 * position} ${343 - i * 6}C${616 - i * 5 * position} ${470 - i * 6} ${684 - i * 5 * position} ${875 - i * 6} ${684 - i * 5 * position} ${875 - i * 6}`,
    width: 0.5 + i * 0.03,
  }));

  return (
    <div className="absolute inset-0 pointer-events-none">
      <svg className="w-full h-full text-slate-950" viewBox="0 0 696 316" fill="none">
        <title>Background</title>
        {paths.map((path) => (
          <motion.path
            key={path.id}
            d={path.d}
            stroke="currentColor"
            strokeWidth={path.width}
            strokeOpacity={0.04 + path.id * 0.015}
            initial={{ pathLength: 0.3, opacity: 0.4 }}
            animate={{
              pathLength: 1,
              opacity: [0.2, 0.4, 0.2],
              pathOffset: [0, 1, 0],
            }}
            transition={{
              duration: 20 + Math.random() * 10,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        ))}
      </svg>
    </div>
  );
}

export default function HomePage() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    getAuthStatus()
      .then((status) => {
        if (status.authenticated) {
          router.push("/convert");
        } else {
          setChecking(false);
        }
      })
      .catch(() => setChecking(false));
  }, [router]);

  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-[#FC4C02] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center overflow-hidden bg-white">
      <Header />

      <div className="absolute inset-0">
        <FloatingPaths position={1} />
        <FloatingPaths position={-1} />
      </div>

      <div className="relative z-10 container mx-auto px-4 text-center pt-16">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5 }}
          className="max-w-5xl mx-auto"
        >
          <motion.h1
            initial={{ y: 40, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.8, type: "spring" }}
            className="text-5xl sm:text-7xl md:text-8xl font-bold mb-6 tracking-tighter"
          >
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FC4C02] via-[#FF6B35] to-[#FC4C02]">
              Trail
            </span>
            <span className="text-foreground">2</span>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FC4C02] via-[#FF6B35] to-[#FC4C02]">
              Strava
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.6 }}
            className="text-lg sm:text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto"
          >
            Seamlessly sync your AllTrails activities to Strava in seconds.
            No manual uploads, no hassle.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1, duration: 0.6 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-4xl mx-auto"
          >
            {steps.map((step, index) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2 + index * 0.15, duration: 0.5 }}
                className="relative group"
              >
                <div className="bg-background/80 backdrop-blur-sm border border-border rounded-2xl p-6 hover:border-[#FC4C02]/50 transition-all duration-300 hover:shadow-lg hover:shadow-[#FC4C02]/10">
                  <div className="flex items-center justify-center w-12 h-12 rounded-full bg-[#FC4C02]/10 text-[#FC4C02] mb-4 mx-auto group-hover:scale-110 transition-transform duration-300">
                    {step.icon}
                  </div>
                  <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-[#FC4C02] text-white flex items-center justify-center font-bold text-sm shadow-lg">
                    {step.number}
                  </div>
                  <h3 className="text-lg font-semibold mb-2 text-foreground">{step.title}</h3>
                  <p className="text-sm text-muted-foreground">{step.description}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.8, duration: 0.6 }}
          >
            <ConnectStravaButton />
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2.2 }}
            className="mt-6 text-xs text-muted-foreground"
          >
            Your data is secure. We only request permission to create activities on your behalf.
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
}
