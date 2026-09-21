import api from "./api";

// =====================================================
// REGISTER USER
// =====================================================

export const registerUser = async (userType, data) => {

  // ===================================================
  // FORM DATA
  // Used for NGO registration because it contains
  // certificate and logo files.
  // ===================================================

  if (data instanceof FormData) {

    // Add user type directly to FormData
    data.append(
      "user_type",
      userType
    );

    console.log(
      "========== REGISTER FORMDATA =========="
    );

    for (const [key, value] of data.entries()) {

      console.log(
        key,
        value
      );

    }

    console.log(
      "======================================="
    );

    // Send FormData directly
    return await api.post(
      "register/",
      data
    );
  }


  // ===================================================
  // NORMAL JSON REGISTRATION
  // Used for normal donor registration.
  // ===================================================

  return await api.post(
    "register/",
    {
      user_type: userType,
      data: data,
    }
  );
};