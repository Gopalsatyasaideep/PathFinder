/**
 * Card Component
 * Reusable card component for displaying content sections
 */
const Card = ({ title, children, className = '' }) => {
  return (
    <div className={`bg-white rounded-lg shadow-md border border-gray-200 p-6 ${className}`}>
      {title && (
        <h3 className="text-xl font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">
          {title}
        </h3>
      )}
      <div className="text-gray-700">{children}</div>
    </div>
  );
};

export default Card;
