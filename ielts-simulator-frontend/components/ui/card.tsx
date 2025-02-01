export function Card({ children }: any) {
    return <div className="border rounded p-4 shadow">{children}</div>;
  }
  
  export function CardContent({ children }: any) {
    return <div>{children}</div>;
  }
  