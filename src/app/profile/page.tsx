"use client";
import { useEffect, useState } from "react";
import { verifyToken } from "@/api";
import { supabase } from "@/lib/supabase";
import { toast } from "sonner";
import Loader from "@/components/ui/loader";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { PencilIcon, CheckIcon, XMarkIcon } from "@heroicons/react/24/solid";

// Force dynamic rendering to prevent prerendering
export const dynamic = "force-dynamic";

export default function ProfilePage() {
  const [profile, setProfile] = useState({
    username: "",
    avatar_url: "",
    name: "",
  });
  const [originalProfile, setOriginalProfile] = useState(profile);
  const [editingField, setEditingField] = useState<null | "name" | "username">(
    null
  );
  const [loading, setLoading] = useState(true);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient) return;

    const fetchProfile = async () => {
      try {
        // Check if Supabase is available
        if (!supabase) {
          toast.error("Service temporarily unavailable");
          setLoading(false);
          return;
        }

        const token = localStorage.getItem("token");
        if (!token) {
          toast.error("Not logged in");
          setLoading(false);
          return;
        }

        const isValid = await verifyToken();
        if (!isValid) {
          toast.error("Session expired. Please log in again.");
          localStorage.removeItem("token");
          localStorage.removeItem("userData");
          setLoading(false);
          return;
        }

        const userData = localStorage.getItem("userData");
        if (userData) {
          const parsedData = JSON.parse(userData);
          const userProfile = {
            username: parsedData.username || "",
            name: parsedData.name || "",
            avatar_url: parsedData.avatar_url || "",
          };

          setProfile(userProfile);
          setOriginalProfile(userProfile);
        }
      } catch (error) {
        console.error("Error fetching profile:", error);
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
      if (!supabase) throw new Error("Service unavailable");

      const user = (await supabase.auth.getUser()).data.user;
      if (!user) throw new Error("Not authenticated");

      const { error } = await supabase
        .from("profiles")
        .update({ [field]: profile[field] })
        .eq("id", user.id);

      if (error) throw error;

      // Actualizar localStorage
      const userData = localStorage.getItem("userData");
      if (userData) {
        const parsedData = JSON.parse(userData);
        parsedData[field] = profile[field];
        localStorage.setItem("userData", JSON.stringify(parsedData));
      }

      toast.success("Profile updated");
      setOriginalProfile({ ...profile });
    } catch (error) {
      console.error("Error updating profile:", error);
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

  if (!isClient || loading)
    return (
      <div className="w-full h-screen flex flex-col items-center justify-center">
        <Loader />
        <p className="text-gray-400 mt-4">Loading profile...</p>
      </div>
    );

  return (
    <div className="max-w-md mx-auto mt-10 p-4 bg-gray-800 rounded-lg space-y-6">
      <h2 className="text-lg font-semibold text-center mb-4 text-white">
        My Profile
      </h2>

      <label className="block text-sm text-gray-300 text-center mb-2">
        Avatar
      </label>
      <div className="flex flex-col items-center mb-6">
        <Avatar className="h-24 w-24 mb-2">
          <AvatarImage
            key={profile.avatar_url}
            src={profile.avatar_url}
            alt={profile.name || profile.username}
          />
          <AvatarFallback className="text-5xl font-medium">
            {(profile.name || profile.username || "?").charAt(0).toUpperCase()}
          </AvatarFallback>
        </Avatar>

        <label
          htmlFor="avatar-upload"
          className="cursor-pointer text-sm text-blue-400 hover:text-blue-300 mt-2"
        >
          Change avatar
          <input
            id="avatar-upload"
            type="file"
            accept="image/*"
            className="hidden"
            onChange={async (e) => {
              try {
                if (e.target.files && e.target.files[0]) {
                  const file = e.target.files[0];
                  const publicUrl = await uploadAvatar(file);

                  // Update profile and localStorage
                  const newProfile = { ...profile, avatar_url: publicUrl };
                  setProfile(newProfile);
                  setOriginalProfile(newProfile);

                  // Update localStorage
                  const userData = localStorage.getItem("userData");
                  if (userData) {
                    const parsedData = JSON.parse(userData);
                    parsedData.avatar_url = publicUrl;
                    localStorage.setItem(
                      "userData",
                      JSON.stringify(parsedData)
                    );
                  }

                  const toastId = toast.loading("Uploading avatar...");
                  await new Promise((resolve) => setTimeout(resolve, 1000));
                  toast.dismiss(toastId);
                  toast.success("Avatar updated successfully");
                }
              } catch (error: Error | unknown) {
                toast.dismiss();
                toast.error(
                  error instanceof Error
                    ? error.message
                    : "Failed to upload avatar"
                );
                console.error("Error uploading avatar:", error);
              }
            }}
          />
        </label>
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
            {profile.name || "Click to add name"}
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
  );
}
