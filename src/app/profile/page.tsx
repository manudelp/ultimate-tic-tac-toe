"use client";
import { useEffect, useState } from "react";
import { verifyToken } from "@/api";
import { toast } from "sonner";
import Loader from "@/components/ui/loader";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { PencilIcon, CheckIcon, XMarkIcon } from "@heroicons/react/24/solid";

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

  useEffect(() => {
    const fetchProfile = async () => {
      try {
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
  }, []);

  const handleSaveField = async (field: "name" | "username") => {
    console.log("Saving field:", field, "current editing field:", editingField);

    // For now, just update localStorage since we don't have a backend profile update endpoint
    try {
      const userData = localStorage.getItem("userData");
      if (userData) {
        const parsedData = JSON.parse(userData);
        parsedData[field] = profile[field];
        localStorage.setItem("userData", JSON.stringify(parsedData));

        toast.success("Profile updated locally");
        setOriginalProfile({ ...profile });
      }
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

  if (loading)
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
      <div className="flex justify-center mb-6">
        <Avatar className="h-24 w-24">
          <AvatarImage
            src={profile.avatar_url}
            alt={profile.name || profile.username}
          />
          <AvatarFallback className="text-5xl font-medium">
            {(profile.name || profile.username || "?").charAt(0).toUpperCase()}
          </AvatarFallback>
        </Avatar>
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
