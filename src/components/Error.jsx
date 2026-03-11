/**
 * Error Component
 * Displays error message with optional retry button
 */
const Error = ({ message = 'Something went wrong', onRetry }) => {
  // Ensure message is always a string
  const errorMessage = typeof message === 'string' 
    ? message 
    : Array.isArray(message)
    ? message.map(m => typeof m === 'string' ? m : JSON.stringify(m)).join(', ')
    : JSON.stringify(message);
  
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="text-red-600 mb-4">
        <svg
          className="w-16 h-16 mx-auto"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      <p className="text-gray-700 text-center mb-4">{errorMessage}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
};

export default Error;
