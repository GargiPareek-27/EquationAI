// frontend/components/ClarificationNeeded.tsx
export default function ClarificationNeeded({ message }: { message: string | null }) {
  return (
    <div className="w-full max-w-2xl p-5 bg-[#2A2515] border border-[#6B5A2E] rounded-lg">
      <div className="flex items-start gap-3">
        <svg className="w-4 h-4 text-[#D4A84E] mt-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <div className="font-serif text-[#D4A84E] mb-1">This problem needs a bit more information</div>
          <div className="text-[#B8AC8E] text-sm">{message || "The problem as stated doesn't provide enough information to solve uniquely."}</div>
        </div>
      </div>
    </div>
  );
}