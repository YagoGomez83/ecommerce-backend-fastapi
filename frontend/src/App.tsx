function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-xl shadow-lg text-center max-w-md w-full border border-gray-200">
        <div className="mb-4">
          <span className="text-4xl">🚀</span>
        </div>
        <h1 className="text-3xl font-bold text-blue-600 mb-2">
          Ecommerce Pro
        </h1>
        <p className="text-gray-500 mb-6">
          Frontend + Backend + Database
          <br />
          <span className="text-sm font-mono text-green-500">System Online</span>
        </p>
        
        <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-300 w-full cursor-pointer">
          Iniciar Sesión
        </button>
      </div>
    </div>
  )
}

export default App