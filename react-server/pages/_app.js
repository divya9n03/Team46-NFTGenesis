/* pages/_app.js */
import '../styles/globals.css'
import Link from 'next/link'

function MyApp({ Component, pageProps }) {
  return (
    <div>
      <link></link>
      <nav className="border-b bg-gray-800 p-6">
        <p className="text-4xl text-purple-700 font-bold">NFT Genesis</p>
        <div className="flex mt-4">
        

          <Link href="/">
            <a className="mr-6 text-white">
              Home
            </a>
          </Link>
          <Link href="/create-nft">
            <a className="mr-6 text-white">
              Sell NFT
            </a>
          </Link>
          <Link href="/my-nfts">
            <a className="mr-6 text-white">
              My NFTs
            </a>
          </Link>
          <Link href="/dashboard">
            <a className="mr-6 text-white">
              Dashboard
            </a>
          </Link>
          <Link href="http://localhost:5000" target="_blank"> 
            <a className="mr-6 text-white" >
              Generate
            </a>
          </Link>
        </div>
      </nav>
      <div>
      <a href="http://localhost:5000"  >
      <video autoPlay muted loop id="logo"style={{ 
        position: 'fixed', 
        bottom: 10, 
        right: 20, 
        width: 'auto', 
        height: 'auto',
        zIndex: 9999,
        borderRadius: '10px'}}>
        <source src="/videos/Logo_resized.mp4" type="video/mp4" />

      </video>
      </a>
      </div>
      <Component {...pageProps} />
    </div>
  )
}

export default MyApp