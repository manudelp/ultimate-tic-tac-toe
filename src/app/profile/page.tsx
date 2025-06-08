"use client";
import { useEffect, useState, useCallback } from "react";
import { supabase, getUserProfileWithLinking } from "@/lib/supabase";
import { toast } from "sonner";
import Loader from "@/components/ui/loader";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { PencilIcon, CheckIcon, XMarkIcon } from "@heroicons/react/24/solid";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { PhotoIcon, TrashIcon } from "@heroicons/react/24/outline";
import Cropper from "react-easy-crop";

// Force dynamic rendering to prevent prerendering
export const dynamic = "force-dynamic";

interface UserProfile {
  username: string;
  avatar_url: string;
  name: string;
}

interface CropArea {
  x: number;
  y: number;
  width: number;
  height: number;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile>({
    username: "",
    avatar_url: "",
    name: "",
  });
  const [originalProfile, setOriginalProfile] = useState<UserProfile>(profile);
  const [editingField, setEditingField] = useState<null | "name" | "username">(
    null
  );
  const [loading, setLoading] = useState(true);
  const [isClient, setIsClient] = useState(false);

  // New state for image cropping
  const [showCropModal, setShowCropModal] = useState(false);
  const [imageToCrop, setImageToCrop] = useState<string>("");
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState<CropArea | null>(
    null
  );
  const [originalFile, setOriginalFile] = useState<File | null>(null);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient) return;

    const fetchProfile = async () => {
      try {
        const {
          data: { user },
          error,
        } = await supabase.auth.getUser();

        if (error || !user) {
          toast.error("Not logged in");
          setLoading(false);
          return;
        }

        // Use enhanced profile loading with linking
        const userData = await getUserProfileWithLinking(user);

        if (!userData) {
          toast.error("Failed to load user data");
          setLoading(false);
          return;
        }

        const userProfile = {
          username: userData.username || "",
          name: userData.name || "",
          avatar_url: userData.avatar_url || "",
        };

        setProfile(userProfile);
        setOriginalProfile(userProfile);
      } catch {
        toast.error("Failed to load profile");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [isClient]);

  async function updateAvatarUrl(userId: string, avatarUrl: string) {
    if (!supabase) throw new Error("Service unavailable");

    const { error } = await supabase
      .from("profiles")
      .update({ avatar_url: avatarUrl })
      .eq("id", userId);

    if (error) {
      throw error;
    }
  }

  const uploadAvatar = async (file: File) => {
    if (!supabase) throw new Error("Service unavailable");

    // Check file size - 1MB limit
    if (file.size > 1024 * 1024) {
      throw new Error("File size exceeds 1MB limit");
    }

    const {
      data: { user },
      error: userError,
    } = await supabase.auth.getUser();
    if (userError || !user) throw new Error("Not authenticated");

    // Convert image to WebP
    const webpFile = await convertToWebP(file);
    const filePath = `${user.id}/avatar.webp`;

    const { error: uploadError } = await supabase.storage
      .from("avatars")
      .upload(filePath, webpFile, { upsert: true });

    if (uploadError) throw uploadError;

    const { data } = supabase.storage.from("avatars").getPublicUrl(filePath);

    if (!data?.publicUrl) throw new Error("Failed to get public URL");

    await updateAvatarUrl(user.id, data.publicUrl);

    return data.publicUrl;
  };

  // Helper function to convert image to WebP
  const convertToWebP = async (file: File): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext("2d");
        ctx?.drawImage(img, 0, 0);
        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob);
            } else {
              reject(new Error("WebP conversion failed"));
            }
          },
          "image/webp",
          0.9
        ); // 0.9 is the quality (90%)
      };
      img.onerror = () => reject(new Error("Failed to load image"));
      img.src = URL.createObjectURL(file);
    });
  };

  const handleSaveField = async (field: "name" | "username") => {
    try {
      const {
        data: { user },
        error: userError,
      } = await supabase.auth.getUser();
      if (userError || !user) throw new Error("Not authenticated");

      // Update Supabase user metadata
      const { error: updateError } = await supabase.auth.updateUser({
        data: { [field]: profile[field] },
      });

      if (updateError) throw updateError;

      // Update profiles table if it exists
      try {
        await supabase
          .from("profiles")
          .upsert({
            id: user.id,
            [field]: profile[field],
          })
          .eq("id", user.id);
      } catch {
        // Continue anyway - the user metadata was updated
      }

      // Update localStorage
      const userData = localStorage.getItem("userData");
      if (userData) {
        const parsedData = JSON.parse(userData);
        parsedData[field] = profile[field];
        localStorage.setItem("userData", JSON.stringify(parsedData));
      }

      toast.success("Profile updated");
      setOriginalProfile({ ...profile });
    } catch {
      toast.error("Failed to update profile");
      setProfile((prev) => ({ ...prev, [field]: originalProfile[field] }));
    }

    setEditingField(null);
  };

  const handleCancelEdit = (e?: React.MouseEvent | React.KeyboardEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    // Restore the original values
    setProfile({ ...originalProfile });
    // Exit edit mode
    setEditingField(null);
  };

  const handleStartEdit = (e: React.MouseEvent, field: "name" | "username") => {
    e.preventDefault();
    e.stopPropagation();

    // Only allow editing one field at a time
    if (editingField && editingField !== field) {
      toast.error("Please finish editing the current field first.");
      return; // Don't start editing if another field is being edited
    }

    setEditingField(field);
  };

  const handleFieldChange = (field: "name" | "username", value: string) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
  };

  const handleSaveClick = (e: React.MouseEvent, field: "name" | "username") => {
    e.preventDefault();
    e.stopPropagation();
    handleSaveField(field);
  };

  const onCropComplete = useCallback(
    (
      croppedArea: { x: number; y: number; width: number; height: number },
      croppedAreaPixels: CropArea
    ) => {
      setCroppedAreaPixels(croppedAreaPixels);
    },
    []
  );

  const createCroppedImage = async (
    imageSrc: string,
    pixelCrop: CropArea
  ): Promise<Blob> => {
    const image = new Image();
    image.src = imageSrc;

    return new Promise((resolve, reject) => {
      image.onload = () => {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");

        if (!ctx) {
          reject(new Error("Could not get canvas context"));
          return;
        }

        // Set canvas size to the crop size
        canvas.width = pixelCrop.width;
        canvas.height = pixelCrop.height;

        // Draw the cropped image
        ctx.drawImage(
          image,
          pixelCrop.x,
          pixelCrop.y,
          pixelCrop.width,
          pixelCrop.height,
          0,
          0,
          pixelCrop.width,
          pixelCrop.height
        );

        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob);
            } else {
              reject(new Error("Canvas toBlob failed"));
            }
          },
          "image/jpeg",
          0.9
        );
      };
      image.onerror = () => reject(new Error("Failed to load image"));
    });
  };

  const handleCropSave = async () => {
    try {
      if (!croppedAreaPixels || !imageToCrop || !originalFile) {
        toast.error("Missing crop data");
        return;
      }

      const croppedBlob = await createCroppedImage(
        imageToCrop,
        croppedAreaPixels
      );

      // Create a new File from the cropped blob
      const croppedFile = new File([croppedBlob], originalFile.name, {
        type: "image/jpeg",
        lastModified: Date.now(),
      });

      // Close modal
      setShowCropModal(false);
      setImageToCrop("");
      setOriginalFile(null);

      // Upload the cropped image
      const toastId = toast.loading("Uploading avatar...");
      const publicUrl = await uploadAvatar(croppedFile);

      // Update profile and localStorage
      const newProfile = { ...profile, avatar_url: publicUrl };
      setProfile(newProfile);
      setOriginalProfile(newProfile);

      // Update localStorage
      const userData = localStorage.getItem("userData");
      if (userData) {
        const parsedData = JSON.parse(userData);
        parsedData.avatar_url = publicUrl;
        localStorage.setItem("userData", JSON.stringify(parsedData));
      }

      toast.dismiss(toastId);
      toast.success("Avatar updated successfully");
    } catch (err: unknown) {
      toast.error(
        err instanceof Error ? err.message : "Failed to upload avatar"
      );
      setShowCropModal(false);
    }
  };

  const handleCropCancel = () => {
    setShowCropModal(false);
    setImageToCrop("");
    setOriginalFile(null);
    setCrop({ x: 0, y: 0 });
    setZoom(1);
    setCroppedAreaPixels(null);
  };

  const handleDeleteAvatar = async () => {
    try {
      const {
        data: { user },
        error: userError,
      } = await supabase.auth.getUser();
      if (userError || !user) throw new Error("Not authenticated");

      // Update Supabase user metadata to remove avatar
      const { error: updateError } = await supabase.auth.updateUser({
        data: { avatar_url: null },
      });

      if (updateError) throw updateError;

      // Update profiles table if it exists
      try {
        await supabase
          .from("profiles")
          .update({ avatar_url: null })
          .eq("id", user.id);
      } catch {
        // Continue anyway - the user metadata was updated
      }

      // Update local state and localStorage
      const newProfile = { ...profile, avatar_url: "" };
      setProfile(newProfile);
      setOriginalProfile(newProfile);

      // Update localStorage
      const userData = localStorage.getItem("userData");
      if (userData) {
        const parsedData = JSON.parse(userData);
        parsedData.avatar_url = "";
        localStorage.setItem("userData", JSON.stringify(parsedData));
      }

      toast.success("Avatar deleted successfully");
    } catch (err: unknown) {
      toast.error(
        err instanceof Error ? err.message : "Failed to delete avatar"
      );
    }
  };

  if (!isClient || loading)
    return (
      <div className="w-full h-screen flex flex-col items-center justify-center">
        <Loader />
        <p className="text-gray-400 mt-4">Loading profile...</p>
      </div>
    );

  return (
    <>
      <div className="max-w-md mx-auto mt-10 p-4 bg-gray-800 rounded-lg space-y-6">
        <h2 className="text-xl font-semibold text-center mb-4 text-white">
          My Profile
        </h2>

        {/* Avatar section */}
        <label className="block text-sm text-gray-300 text-center mb-2">
          Avatar
        </label>
        <div className="flex flex-col items-center mb-6">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <div className="relative cursor-pointer group">
                <Avatar className="h-24 w-24 mb-2 transition-opacity group-hover:opacity-80">
                  <AvatarImage
                    key={profile.avatar_url}
                    src={profile.avatar_url}
                    alt={profile.name || profile.username}
                  />
                  <AvatarFallback className="text-5xl font-medium">
                    {(profile.name || profile.username || "?")
                      .charAt(0)
                      .toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="absolute top-0 left-0 w-24 h-24 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black bg-opacity-30 rounded-full">
                  <PencilIcon className="w-6 h-6 text-white" />
                </div>
              </div>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-48 bg-gray-800 border-gray-700">
              <DropdownMenuItem
                onClick={() =>
                  document.getElementById("avatar-upload")?.click()
                }
                className="flex items-center gap-2 text-gray-300 hover:text-white hover:bg-gray-700 cursor-pointer"
              >
                <PhotoIcon className="w-4 h-4" />
                {profile.avatar_url ? "Replace image" : "Add image"}
              </DropdownMenuItem>
              {profile.avatar_url && (
                <DropdownMenuItem
                  onClick={handleDeleteAvatar}
                  className="flex items-center gap-2 text-red-400 hover:text-red-300 hover:bg-gray-700 cursor-pointer"
                >
                  <TrashIcon className="w-4 h-4" />
                  Delete image
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Hidden file input */}
          <input
            id="avatar-upload"
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                const file = e.target.files[0];

                // Check file size - 5MB limit for original file
                if (file.size > 5 * 1024 * 1024) {
                  toast.error("File size exceeds 5MB limit");
                  return;
                }

                setOriginalFile(file);
                const reader = new FileReader();
                reader.onload = () => {
                  setImageToCrop(reader.result as string);
                  setShowCropModal(true);
                };
                reader.readAsDataURL(file);
              }
              // Reset the input value
              e.target.value = "";
            }}
          />
        </div>

        {/* Name Field */}
        <div className="space-y-1">
          <div className="text-sm text-gray-300 flex justify-between items-center">
            <span>Name</span>
            <div className="flex gap-2">
              {editingField === "name" ? (
                <>
                  <button
                    type="button"
                    onClick={(e) => handleSaveClick(e, "name")}
                    className="w-5 h-5 text-green-400 hover:text-green-600 transition-colors"
                    title="Save changes"
                  >
                    <CheckIcon />
                  </button>
                  <button
                    type="button"
                    onClick={handleCancelEdit}
                    className="w-5 h-5 text-red-400 hover:text-red-600 transition-colors"
                    title="Cancel changes"
                  >
                    <XMarkIcon />
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  onClick={(e) => handleStartEdit(e, "name")}
                  className="w-5 h-5 text-gray-400 hover:text-white transition-colors"
                  title="Click to edit name"
                >
                  <PencilIcon />
                </button>
              )}
            </div>
          </div>
          {editingField === "name" ? (
            <input
              type="text"
              className="w-full px-3 py-2 bg-gray-600 text-white border border-gray-500 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={profile.name}
              onChange={(e) => handleFieldChange("name", e.target.value)}
              placeholder="Enter your name"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  handleSaveField("name");
                } else if (e.key === "Escape") {
                  e.preventDefault();
                  handleCancelEdit(e);
                }
              }}
            />
          ) : (
            <div className="w-full px-3 py-2 bg-gray-700 text-gray-300 border border-gray-600 rounded-md cursor-not-allowed hover:bg-gray-650 transition-colors">
              {profile.name || "Name"}
            </div>
          )}
        </div>

        {/* Username Field */}
        <div className="space-y-1">
          <div className="text-sm text-gray-300 flex justify-between items-center">
            <span>Username</span>
            <div className="flex gap-2">
              {editingField === "username" ? (
                <>
                  <button
                    type="button"
                    onClick={(e) => handleSaveClick(e, "username")}
                    className="w-5 h-5 text-green-400 hover:text-green-600 transition-colors"
                    title="Save changes"
                  >
                    <CheckIcon />
                  </button>
                  <button
                    type="button"
                    onClick={handleCancelEdit}
                    className="w-5 h-5 text-red-400 hover:text-red-600 transition-colors"
                    title="Cancel changes"
                  >
                    <XMarkIcon />
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  onClick={(e) => handleStartEdit(e, "username")}
                  className="w-5 h-5 text-gray-400 hover:text-white transition-colors"
                  title="Click to edit username"
                >
                  <PencilIcon />
                </button>
              )}
            </div>
          </div>
          {editingField === "username" ? (
            <input
              type="text"
              className="w-full px-3 py-2 bg-gray-600 text-white border border-gray-500 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={profile.username}
              onChange={(e) => handleFieldChange("username", e.target.value)}
              placeholder="Enter your username"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleSaveField("username");
                } else if (e.key === "Escape") {
                  handleCancelEdit(e);
                }
              }}
            />
          ) : (
            <div className="w-full px-3 py-2 bg-gray-700 text-gray-300 border border-gray-600 rounded-md cursor-not-allowed hover:bg-gray-650 transition-colors">
              {profile.username}
            </div>
          )}
        </div>
      </div>

      {/* Crop Modal */}
      {showCropModal && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg w-full max-w-md mx-auto">
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-lg font-semibold text-white">Crop Avatar</h3>
            </div>

            <div className="relative h-64 bg-gray-900">
              <Cropper
                image={imageToCrop}
                crop={crop}
                zoom={zoom}
                aspect={1}
                onCropChange={setCrop}
                onZoomChange={setZoom}
                onCropComplete={onCropComplete}
                cropShape="round"
                showGrid={false}
              />
            </div>

            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm text-gray-300 mb-2">Zoom</label>
                <input
                  type="range"
                  min={1}
                  max={3}
                  step={0.1}
                  value={zoom}
                  onChange={(e) => setZoom(Number(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                />
              </div>

              <div className="flex gap-3 justify-end">
                <button
                  onClick={handleCropCancel}
                  className="px-4 py-2 text-gray-300 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCropSave}
                  className="px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
                >
                  Save Avatar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
