import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Image from "next/image";
import { toast } from "sonner";
import { loginUser, registerUser } from "@/api";

export function LoginForm() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (isLogin) {
        // Iniciar sesión
        const { access_token, name } = await loginUser(
          formData.email,
          formData.password
        );
        window.location.reload(); // Recargar la página tras login
        toast.success(`Welcome back, ${name}!`);

        // Guardar el nombre del usuario en localStorage
        localStorage.setItem("name", name);
        localStorage.setItem("token", access_token);
      } else {
        // Validar contraseñas coinciden en el registro
        if (formData.password !== formData.confirmPassword) {
          toast.error("Passwords do not match!");
          return;
        }

        // Registrar usuario
        const response = await registerUser(
          formData.username,
          formData.email,
          formData.password
        );
        toast.success(response.message);
        setIsLogin(true); // Cambiar al formulario de login tras registro
      }
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Something went wrong!"
      );
    }
  };

  return (
    <div className="flex flex-col items-center justify-center p-4 bg-gray-800 rounded-lg text-white">
      <div className="w-full max-w-md p-4 space-y-6">
        <h2 className="text-2xl font-bold text-center">
          {isLogin ? "Welcome Back!" : "Create Your Account"}
        </h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          {!isLogin && (
            <div>
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                required
                className="bg-gray-700 text-white"
                value={formData.username}
                onChange={handleChange}
              />
            </div>
          )}
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="Enter your email"
              required
              className="bg-gray-700 text-white"
              value={formData.email}
              onChange={handleChange}
            />
          </div>
          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter your password"
              required
              className="bg-gray-700 text-white"
              value={formData.password}
              onChange={handleChange}
            />
          </div>
          {!isLogin && (
            <div>
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                required
                className="bg-gray-700 text-white"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
            </div>
          )}
          <Button type="submit" className="w-full bg-gray-700 text-white">
            {isLogin ? "Login" : "Sign Up"}
          </Button>
        </form>

        {/* Separador visual */}
        <div className="flex items-center justify-center space-x-2 my-4">
          <div className="w-1/4 h-px bg-gray-600"></div>
          <p className="text-sm text-gray-400">OR</p>
          <div className="w-1/4 h-px bg-gray-600"></div>
        </div>

        {/* Botón de Google Sign-In */}
        <Button
          className="w-full bg-white text-black flex items-center justify-center gap-2 p-2 rounded-md shadow-md hover:bg-gray-700 hover:text-white transition"
          onClick={() => toast.info("Google Sign-In is coming soon!")}
        >
          <Image
            src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg"
            alt="Google Logo"
            className="w-5 h-5"
            width={20}
            height={20}
          />
          {isLogin ? "Continue with Google" : "Sign up with Google"}
        </Button>

        <div className="flex items-center justify-between">
          <a href="#" className="text-sm text-gray-400 hover:underline">
            Forgot your password?
          </a>
          <button
            type="button"
            className="text-sm text-gray-400 hover:underline"
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? "Sign up" : "Login instead"}
          </button>
        </div>
      </div>
    </div>
  );
}
