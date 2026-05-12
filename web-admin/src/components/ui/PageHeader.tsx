export function PageHeader({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h2 className="text-2xl font-black tracking-tight text-slate-950">{title}</h2>
        {description ? <p className="mt-1 text-sm font-medium text-slate-500">{description}</p> : null}
      </div>
      {action}
    </div>
  );
}
