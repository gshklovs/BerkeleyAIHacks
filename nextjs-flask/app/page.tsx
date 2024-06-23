import Image from 'next/image'
import Link from 'next/link'

export default function Home() {
  return (<div>
    <button className="h-screen flex justify-screen" >
      <Link href="/yapping"> Start Recording
      </Link>
    </button>
    </div>
  )
}
