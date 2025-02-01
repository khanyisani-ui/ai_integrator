export function Input({ value, onChange, placeholder }: any) {
    return (
      <input
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="border p-2 rounded w-full"
      />
    );
  }
  