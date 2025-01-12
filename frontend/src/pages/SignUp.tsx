import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { AuthService } from "../client/services/services";
import { TSignUpForm } from "../client/models/models";

export default function SignUp() {
  const {
    register: formRegister,
    handleSubmit,
    formState: { errors },
    setError: setFormError,
  } = useForm<TSignUpForm>();
  const navigate = useNavigate();

  const onSubmit = async (formData: TSignUpForm) => {
    try {
      const response = await AuthService.signUp(formData);
      if (response.username) {
        navigate("/login");
      }
    } catch (err) {
      setFormError("root", {
        type: "manual",
        message: "Registration failed",
      });
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="w-full max-w-md space-y-8 rounded-lg bg-white p-8 shadow-lg"
      >
        <h1 className="mb-6 text-2xl font-bold">Sign Up</h1>

        {errors.root && (
          <div className="mb-4 text-red-500">{errors.root.message}</div>
        )}

        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium">Username</label>
          <input
            {...formRegister("username", { required: "Username is required" })}
            className={`w-full rounded border px-3 py-2 ${
              errors.username ? "border-red-500" : "border-gray-300"
            } focus:outline-none focus:ring-2 focus:ring-blue-500`}
          />
          {errors.username && (
            <p className="mt-1 text-sm text-red-500">
              {errors.username.message}
            </p>
          )}
        </div>

        <div className="mb-6">
          <label className="mb-1 block text-sm font-medium">Password</label>
          <input
            type="password"
            {...formRegister("password", { required: "Password is required" })}
            className={`w-full rounded border px-3 py-2 ${
              errors.password ? "border-red-500" : "border-gray-300"
            } focus:outline-none focus:ring-2 focus:ring-blue-500`}
          />
          {errors.password && (
            <p className="mt-1 text-sm text-red-500">
              {errors.password.message}
            </p>
          )}
        </div>

        <button
          type="submit"
          className="w-full rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Sign Up
        </button>
      </form>
    </div>
  );
}
