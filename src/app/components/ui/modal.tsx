import React from "react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-md"
        onClick={(e) => e.stopPropagation()} // Evita que el modal se cierre al hacer clic en su contenido
      >
        {/* Botón de cierre posicionado dentro del contenedor */}
        <button
          className="absolute top-2 right-2 z-10 w-10 h-10 text-white rounded-full hover:bg-red-600 hover:text-white transition"
          onClick={onClose}
        >
          <span className="text-3xl">&times;</span>
        </button>
        {/* Contenido dinámico del modal */}
        <div className="relative">{children}</div>
      </div>
    </div>
  );
};
