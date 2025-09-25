export const Step = ({
  n,
  title,
  desc,
}: {
  n: number;
  title: string;
  desc: string;
}) => (
  <div className="relative flex gap-4">
    <div className="flex h-9 w-9 flex-none items-center justify-center rounded-xl border border-neutral-800 bg-neutral-900 font-semibold">
      {n}
    </div>
    <div>
      <h4 className="text-base font-semibold leading-tight">{title}</h4>
      <p className="mt-1 text-sm text-yellow-300">{desc}</p>
    </div>
  </div>
);
