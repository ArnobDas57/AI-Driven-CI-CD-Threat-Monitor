/* eslint-disable @typescript-eslint/no-explicit-any */
import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export const Feature = ({
  icon: Icon,
  title,
  desc,
}: {
  icon: any;
  title: string;
  desc: string;
}) => (
  <Card className="group relative overflow-hidden border-neutral-800/60 bg-neutral-900/60 backdrop-blur-sm hover:bg-neutral-900 transition-colors">
    <div className="pointer-events-none absolute -inset-px bg-gradient-to-tr from-purple-500/20 via-fuchsia-500/10 to-cyan-400/10 opacity-0 group-hover:opacity-100 transition-opacity" />
    <CardHeader className="pb-2">
      <div className="flex items-center gap-3">
        <div className="rounded-2xl border border-neutral-800 bg-neutral-950 p-2">
          <Icon className="h-5 w-5" />
        </div>
        <CardTitle className="text-lg text-neutral-300">{title}</CardTitle>
      </div>
    </CardHeader>
    <CardContent>
      <CardDescription className="text-neutral-300">{desc}</CardDescription>
    </CardContent>
  </Card>
);
