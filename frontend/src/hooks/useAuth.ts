import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useToast from "./useToast";
import { useMutation, useQuery } from "react-query";
import { AuthService } from "../client/services/auth";
import { TLoginForm } from "../client/api/models/request";

export function useAuth() {
  const [error, setError] = useState(false);
  const navigate = useNavigate();
  const toast = useToast({
    position: "top-right",
    autoClose: 2000,
    closeOnClick: true,
    hideProgressBar: true,
    pauseOnHover: true,
  });
  const isLoggedIn = () => {
    return localStorage.getItem("access_token") !== null;
  };
  const login = async (formData: TLoginForm) => {
    const response = await AuthService.login(formData);
    localStorage.setItem("access_token", response.access_token);
  };
  const { data: user, isLoading } = useQuery({
    queryKey: ["auth"],
    queryFn: () => {
      AuthService.readUser;
    },
    enabled: isLoggedIn(),
  });

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      toast.success("Login successful");
      navigate("/dashboard");
    },
    onError: () => {
      toast.error("Login failed");
    },
  });
  return { user, isLoading, isLoggedIn, loginMutation };
}
