import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Image as ImageIcon, Sparkles } from 'lucide-react';
import { VehicleGallery, VehicleImageItem } from '../../types/chat';

interface VehicleGalleryCardProps {
  gallery: VehicleGallery;
}

export const VehicleGalleryCard: React.FC<VehicleGalleryCardProps> = ({ gallery }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'exterior' | 'interior'>('all');

  const { vehicle, images } = gallery;

  const filteredImages = selectedCategory === 'all'
    ? images
    : images.filter(img => img.category === selectedCategory);

  const activeImages = filteredImages.length > 0 ? filteredImages : images;
  const currentImage: VehicleImageItem = activeImages[currentIndex] || activeImages[0];

  const handlePrev = () => {
    setCurrentIndex((prev) => (prev === 0 ? activeImages.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev === activeImages.length - 1 ? 0 : prev + 1));
  };

  if (!images || images.length === 0) return null;

  return (
    <div className="my-4 rounded-2xl overflow-hidden border border-zinc-700/80 bg-zinc-900/90 shadow-xl max-w-2xl">
      {/* Header */}
      <div className="px-4 py-3 bg-zinc-800/80 border-b border-zinc-700/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <ImageIcon className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-semibold text-sm text-zinc-100 flex items-center gap-1.5">
              {vehicle.manufacturer} {vehicle.model}
              {vehicle.tagline && (
                <span className="text-xs font-normal text-zinc-400 hidden sm:inline">
                  — {vehicle.tagline}
                </span>
              )}
            </h4>
          </div>
        </div>

        {/* Category Filter Tabs */}
        <div className="flex items-center gap-1 bg-zinc-900/80 p-1 rounded-lg border border-zinc-700/50">
          {(['all', 'exterior', 'interior'] as const).map((cat) => (
            <button
              key={cat}
              onClick={() => {
                setSelectedCategory(cat);
                setCurrentIndex(0);
              }}
              className={`px-2 py-0.5 text-xs rounded font-medium capitalize transition ${
                selectedCategory === cat
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Main Image Viewport with 16:9 Aspect Ratio */}
      <div className="relative aspect-video w-full bg-zinc-950 overflow-hidden group">
        <img
          src={currentImage.url}
          alt={currentImage.alt}
          loading="lazy"
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />

        {/* Category Badge */}
        <div className="absolute top-3 left-3 bg-black/60 backdrop-blur-md px-2.5 py-1 rounded-full text-[11px] font-medium text-zinc-200 border border-white/10 uppercase tracking-wider flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-amber-400" />
          {currentImage.category}
        </div>

        {/* Image Counter */}
        <div className="absolute top-3 right-3 bg-black/60 backdrop-blur-md px-2 py-0.5 rounded-full text-[11px] font-mono text-zinc-300 border border-white/10">
          {currentIndex + 1} / {activeImages.length}
        </div>

        {/* Left / Right Nav Arrows */}
        {activeImages.length > 1 && (
          <>
            <button
              onClick={handlePrev}
              aria-label="Previous vehicle image"
              className="absolute left-2.5 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/50 hover:bg-black/80 text-white backdrop-blur-sm opacity-80 hover:opacity-100 transition shadow-lg"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={handleNext}
              aria-label="Next vehicle image"
              className="absolute right-2.5 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/50 hover:bg-black/80 text-white backdrop-blur-sm opacity-80 hover:opacity-100 transition shadow-lg"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </>
        )}

        {/* Caption Overlay */}
        <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-3 pt-6">
          <p className="text-xs text-zinc-200 font-medium text-center">
            {currentImage.caption}
          </p>
        </div>
      </div>

      {/* Thumbnail Strip */}
      {activeImages.length > 1 && (
        <div className="p-2.5 bg-zinc-950/70 border-t border-zinc-800 flex items-center gap-2 overflow-x-auto">
          {activeImages.map((img, idx) => (
            <button
              key={img.id || idx}
              onClick={() => setCurrentIndex(idx)}
              className={`relative shrink-0 w-16 h-10 rounded-lg overflow-hidden border transition-all ${
                currentIndex === idx
                  ? 'border-indigo-500 ring-2 ring-indigo-500/40 opacity-100 scale-105'
                  : 'border-zinc-800 opacity-60 hover:opacity-100'
              }`}
            >
              <img src={img.url} alt={img.alt} className="w-full h-full object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
