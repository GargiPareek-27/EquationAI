// frontend/components/ClarificationNeeded.tsx
export default function ClarificationNeeded({ message }: { message: string | null }) {
  return (
    <div className="w-full max-w-2xl p-5 bg-amber-50 border-l-4 border-amber-500 rounded-r-lg">
      <div className="flex items-start gap-3">
        <span className="text-amber-600 text-xl">💭</span>
        <div>
          <div className="font-semibold text-amber-900 mb-1">This problem needs a bit more information</div>
          <div className="text-amber-800">{message || "The problem as stated doesn't provide enough information to solve uniquely."}</div>
        </div>
      </div>
    </div>
  );
}