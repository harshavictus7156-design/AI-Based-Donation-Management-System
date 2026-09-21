


import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import "./DonateItem.css";

function DonateItem() {
  const navigate = useNavigate();

  // =====================================================
  // LOGGED-IN DONOR
  // =====================================================

  const donorName = localStorage.getItem("user_name");
  const donorEmail = localStorage.getItem("user_email");

  // =====================================================
  // FORM DATA
  // =====================================================

  const [formData, setFormData] = useState({
    ngo: "",
    location: "",
    item_image: null,
    pickup_date: "",
    pickup_time: "",
    pickup_notes: "",
  });

  // Location selection
  const [locationMode, setLocationMode] = useState("registered");
  const [registeredLocation, setRegisteredLocation] = useState("");

  useEffect(() => {
    const savedLocation =
      localStorage.getItem("user_location") ||
      localStorage.getItem("location") ||
      localStorage.getItem("user_address") ||
      localStorage.getItem("address") ||
      "";

    setRegisteredLocation(savedLocation);

    if (savedLocation) {
      setFormData((prev) => ({
        ...prev,
        location: savedLocation,
      }));
      setLocationMode("registered");
    } else {
      setLocationMode("different");
    }
  }, []);

  // =====================================================
  // ITEM DETECTION
  // =====================================================

  const [aiItems, setAiItems] = useState([]);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");

  // =====================================================
  // NGO DATA
  // =====================================================

  const [ngos, setNgos] = useState([]);
  const [ngoLoading, setNgoLoading] = useState(true);
  const [ngoError, setNgoError] = useState("");

  // =====================================================
  // IMAGE
  // =====================================================

  const [imagePreview, setImagePreview] = useState(null);

  // =====================================================
  // DONATION
  // =====================================================

  const [loading, setLoading] = useState(false);

  // Donation created temporarily before matching
  const [donationId, setDonationId] = useState(null);

  // =====================================================
  // MATCHING
  // =====================================================

  const [matchMode, setMatchMode] = useState("");

  const [matchingLoading, setMatchingLoading] =
    useState(false);

  const [matchingError, setMatchingError] =
    useState("");

  const [matchingNGOs, setMatchingNGOs] =
    useState([]);

  const [aiRecommendation, setAiRecommendation] =
    useState(null);

  const [selectedMatch, setSelectedMatch] =
    useState(null);

  // =====================================================
  // ALLOCATION
  // =====================================================

  const [allocationLoading, setAllocationLoading] =
    useState(false);

  const [allocationSuccess, setAllocationSuccess] =
    useState(null);

  // =====================================================
  // FETCH APPROVED NGOS
  // =====================================================

  useEffect(() => {
    const fetchNGOs = async () => {
      try {
        setNgoLoading(true);
        setNgoError("");

        const token =
          localStorage.getItem("access");

        if (!token) {
          setNgoError(
            "Please login first."
          );
          return;
        }

        const response =
          await api.get("ngos/");

        console.log(
          "NGO Response:",
          response.data
        );

        if (
          Array.isArray(response.data)
        ) {
          setNgos(response.data);
        } else {
          setNgoError(
            "Invalid NGO data received from server."
          );
        }

      } catch (error) {
        console.error(
          "NGO FETCH ERROR:",
          error
        );

        if (
          error.response?.status === 401
        ) {
          setNgoError(
            "Your login session has expired. Please login again."
          );
        } else if (
          error.response?.status === 403
        ) {
          setNgoError(
            "You do not have permission to view NGOs."
          );
        } else {
          setNgoError(
            "Unable to connect to backend server."
          );
        }

      } finally {
        setNgoLoading(false);
      }
    };

    fetchNGOs();
  }, []);

  // =====================================================
  // LOCATION
  // =====================================================

  const handleLocationModeChange = (mode) => {
    setLocationMode(mode);

    if (mode === "registered") {
      if (!registeredLocation) {
        setLocationMode("different");

        setFormData((prev) => ({
          ...prev,
          location: "",
        }));

        return;
      }

      setFormData((prev) => ({
        ...prev,
        location: registeredLocation,
      }));

    } else {
      setFormData((prev) => ({
        ...prev,
        location: "",
      }));
    }
  };

  // =====================================================
  // HANDLE INPUT
  // =====================================================

  const handleChange = (e) => {
    const {
      name,
      value,
      files
    } = e.target;

    if (files) {
      const file = files[0];

      setFormData((prev) => ({
        ...prev,
        [name]: file
      }));

      // New image resets everything
      setAiItems([]);
      setAiError("");

      setMatchMode("");
      setMatchingNGOs([]);
      setAiRecommendation(null);
      setSelectedMatch(null);
      setMatchingError("");

      // New image means new donation
      setDonationId(null);

      if (file) {
        setImagePreview(
          URL.createObjectURL(file)
        );
      } else {
        setImagePreview(null);
      }

    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value
      }));
    }
  };

  // =====================================================
  // NORMALIZE ITEM NAME
  // =====================================================

  const normalizeItemName = (itemName) => {
    if (!itemName) return "";

    return String(itemName)
      .trim()
      .replace(/[-_]+/g, " ")
      .replace(/\\s+/g, " ");
  };

  // =====================================================
  // NORMALIZE CATEGORY
  // =====================================================

  const normalizeCategory = (category) => {
    if (!category) {
      return "Other";
    }

    const value = String(category)
      .trim()
      .replace(/[-_]+/g, " ")
      .replace(/\\s+/g, " ")
      .toLowerCase();

    const categoryMap = {
      clothing: "Clothing",
      clothes: "Clothing",
      cloth: "Clothing",

      book: "Books",
      books: "Books",

      food: "Food",
      foods: "Food",

      electronic: "Electronics",
      electronics: "Electronics",

      furniture: "Furniture",

      medical: "Medical Supplies",
      "medical supplies": "Medical Supplies",

      school: "School Supplies",
      "school supplies": "School Supplies",
      education: "School Supplies",
      stationery: "School Supplies",

      other: "Other",
    };

    return categoryMap[value] || "Other";
  };

  // =====================================================
  // IMAGE ANALYSIS
  // =====================================================

  const handleAnalyzeImage = async () => {
    if (!formData.item_image) {
      setAiError(
        "Please upload a donation image first."
      );
      return;
    }

    try {
      setAiLoading(true);
      setAiError("");

      setAiItems([]);

      setMatchMode("");
      setMatchingNGOs([]);
      setAiRecommendation(null);
      setSelectedMatch(null);
      setMatchingError("");

      setDonationId(null);

      const imageData =
        new FormData();

      imageData.append(
        "image",
        formData.item_image
      );

      const response =
        await api.post(
          "donation/analyze/",
          imageData,
          {
            headers: {
              "Content-Type":
                "multipart/form-data"
            }
          }
        );

      console.log(
        "AI RESPONSE:",
        response.data
      );

      const data =
        response.data;

      let detectedItems = [];

      if (
        Array.isArray(data.items)
      ) {
        detectedItems =
          data.items;
      }

      // Backup single item
      if (
        detectedItems.length === 0 &&
        (
          data.item ||
          data.item_name ||
          data.detected_item
        )
      ) {
        detectedItems = [
          {
            item: normalizeItemName(
              data.item ||
              data.item_name ||
              data.detected_item
            ),

            category:
              normalizeCategory(
                data.category
              ),

            quantity:
              Number(data.quantity) || 1,

            confidence:
              data.confidence ?? null
          }
        ];
      }

      if (
        detectedItems.length === 0
      ) {
        setAiError(
          "AI could not detect any donation items from this image."
        );
        return;
      }

      const cleanedItems =
        detectedItems.map(
          (item, index) => ({
            id: index,

            item: normalizeItemName(
              item.item ||
              item.item_name ||
              item.name ||
              "Unknown item"
            ),

            category:
              normalizeCategory(
                item.category
              ),

            quantity:
              Number(
                item.quantity
              ) || 1,

            confidence:
              item.confidence ??
              null
          })
        );

      setAiItems(
        cleanedItems
      );

    } catch (error) {
      console.error(
        "AI ANALYSIS ERROR:",
        error
      );

      console.error(
        "Response:",
        error.response?.data
      );

      setAiError(
        error.response?.data?.detail ||
        "Unable to analyze the image. Please try again."
      );

    } finally {
      setAiLoading(false);
    }
  };

  // =====================================================
  // TOTAL QUANTITY
  // =====================================================

  const totalQuantity =
    aiItems.reduce(
      (total, item) =>
        total +
        Number(
          item.quantity || 0
        ),
      0
    );

  // =====================================================
  // MAIN DETECTED ITEM
  // =====================================================

  const mainDetectedItem =
    aiItems.length > 0
      ? aiItems[0]
      : null;

  // =====================================================
  // CREATE DONATION FOR MATCHING
  // =====================================================

  const createDonationForMatching =
    async () => {

      if (donationId) {
        return donationId;
      }

      if (!formData.item_image) {
        throw new Error(
          "Please upload an item image."
        );
      }

      if (aiItems.length === 0) {
        throw new Error(
          "Please analyze the image first."
        );
      }

      if (!formData.location.trim()) {
        throw new Error(
          "Please enter the pickup location first."
        );
      }

      if (!formData.pickup_date || !formData.pickup_time) {
        throw new Error(
          "Please select the pickup date and pickup time."
        );
      }

      const selectedPickupTime = new Date(
        `${formData.pickup_date}T${formData.pickup_time}:00`
      );

      if (
        Number.isNaN(selectedPickupTime.getTime()) ||
        selectedPickupTime.getTime() <= Date.now()
      ) {
        throw new Error(
          "Pickup date and time must be in the future."
        );
      }

      const data =
        new FormData();

      // -------------------------------------------------
      // IMPORTANT
      // -------------------------------------------------
      // NGO is intentionally NOT sent here.
      //
      // Donation is first created as a draft.
      // After creation we receive donation ID.
      // Then matching APIs use that ID.
      // -------------------------------------------------

      const itemName =
        aiItems
          .map((item) =>
            normalizeItemName(item.item)
          )
          .filter(Boolean)
          .join(", ");

      const categories = [
        ...new Set(
          aiItems.map(
            (item) =>
              normalizeCategory(
                item.category
              )
          )
        )
      ];

      const category =
        categories.length === 1
          ? categories[0]
          : "Other";

      const description =
        aiItems
          .map(
            (item) =>
              `${item.item} × ${item.quantity}`
          )
          .join(", ");

      data.append(
        "item_name",
        itemName
      );

      data.append(
        "category",
        category || "Other"
      );

      data.append(
        "quantity",
        String(Number(totalQuantity) || 1)
      );

      // Backend requires condition.
      // Use a valid Donation condition choice.
      data.append(
        "condition",
        "Good"
      );

      data.append(
        "description",
        description || "Donation item"
      );

      data.append(
        "location",
        formData.location.trim()
      );

      data.append(
        "item_image",
        formData.item_image
      );

      console.log("========== DONATION PAYLOAD ==========");
      console.log("Detected items:", aiItems);
      console.log("item_name:", itemName);
      console.log("category:", category);
      console.log("quantity:", totalQuantity);

      // Do NOT send NGO here.
      // Backend model allows ngo = null.

      const response =
        await api.post(
          "donation/",
          data,
          {
            headers: {
              "Content-Type":
                "multipart/form-data"
            }
          }
        );

      console.log(
        "DRAFT DONATION CREATED:",
        response.data
      );

      const newDonationId =
        response.data?.id;

      if (!newDonationId) {
        throw new Error(
          "Donation was created but donation ID was not returned by backend."
        );
      }

      setDonationId(
        newDonationId
      );

      return newDonationId;
    };

  // =====================================================
  // START MATCHING
  // =====================================================

  const handleMatching = async (
    mode
  ) => {

    if (
      aiItems.length === 0
    ) {
      alert(
        "Please analyze the donation image first."
      );
      return;
    }

    if (
      !formData.location.trim()
    ) {
      alert(
        "Please enter the pickup location first."
      );
      return;
    }

    try {
      setMatchMode(mode);
      setMatchingLoading(true);
      setMatchingError("");

      setMatchingNGOs([]);
      setAiRecommendation(null);
      setSelectedMatch(null);

      // -------------------------------------------------
      // STEP 1
      // Create donation and get ID
      // -------------------------------------------------

      const id =
        await createDonationForMatching();

      // -------------------------------------------------
      // STEP 2
      // DONOR MATCHING
      // -------------------------------------------------

      if (mode === "donor") {

        const response =
          await api.get(
            `donation/${id}/matching-ngos/`
          );

        console.log(
          "DONOR MATCH RESPONSE:",
          response.data
        );

        const data =
          response.data;

        const matches =
          data.matching_ngos ||
          data.ngos ||
          data.results ||
          [];

        setMatchingNGOs(
          Array.isArray(matches)
            ? matches
            : []
        );
      }

      // -------------------------------------------------
      // STEP 3
      // AUTOMATIC MATCHING
      // -------------------------------------------------

      if (mode === "ai") {

        const response =
          await api.get(
            `donation/${id}/ai-matching/`
          );

        console.log(
          "AI MATCH RESPONSE:",
          response.data
        );

        const data =
          response.data;

        setAiRecommendation(
          data.ai_recommendation ||
          data.recommended_ngo ||
          null
        );

        const otherMatches =
          data.other_matching_ngos ||
          data.matching_ngos ||
          data.ngos ||
          data.results ||
          [];

        setMatchingNGOs(
          Array.isArray(otherMatches)
            ? otherMatches
            : []
        );
      }

    } catch (error) {

      console.error(
        "========== MATCHING ERROR =========="
      );

      console.error(
        "STATUS:",
        error.response?.status
      );

      console.error(
        "URL:",
        error.config?.url
      );

      console.error(
        "METHOD:",
        error.config?.method
      );

      console.error(
        "RESPONSE:",
        error.response?.data
      );

      console.error(
        "FULL ERROR:",
        error
      );

      const responseData =
        error.response?.data;

      let message =
        "Unable to find matching NGOs.";

      if (typeof responseData === "string") {

        message = responseData;

      } else if (responseData?.detail) {

        message = responseData.detail;

      } else if (responseData?.message) {

        message = responseData.message;

      } else if (
        responseData &&
        typeof responseData === "object"
      ) {

        message =
          Object.entries(responseData)
            .map(([field, value]) => {

              const valueText =
                Array.isArray(value)
                  ? value.join(", ")
                  : typeof value === "object" &&
                    value !== null
                    ? JSON.stringify(value)
                    : String(value);

              return `${field}: ${valueText}`;
            })
            .join(" | ");

      } else if (error.response?.status) {

        message =
          `Request failed with status code ${error.response.status}`;

      } else {

        message =
          error.message ||
          message;
      }

      setMatchingError(message);

    } finally {
      setMatchingLoading(false);
    }
  };

  // =====================================================
  // SELECT NGO
  // =====================================================

  const handleSelectNGO = (
    ngo
  ) => {

    const ngoId =
      ngo.ngo_id ||
      ngo.id ||
      ngo.ngo;

    if (!ngoId) {
      alert(
        "NGO ID was not received."
      );
      return;
    }

    setSelectedMatch(
      ngo
    );

    setFormData((prev) => ({
      ...prev,
      ngo: ngoId
    }));
  };

  // =====================================================
  // SELECTED NGO QUANTITY
  // =====================================================

  const getSelectedQuantity = () => {

    if (!selectedMatch) {
      return totalQuantity;
    }

    const remaining =
      Number(
        selectedMatch.remaining_need ??
        selectedMatch.remaining_quantity ??
        selectedMatch.required_quantity ??
        totalQuantity
      );

    return Math.min(
      totalQuantity,
      remaining
    );
  };

  // =====================================================
  // FINAL SUBMIT / ALLOCATION
  // =====================================================

  const handleSubmit = async (e) => {

    e.preventDefault();

    if (!formData.item_image) {
      alert(
        "Please upload an item image."
      );
      return;
    }

    if (aiItems.length === 0) {
      alert(
        "Please analyze the image first."
      );
      return;
    }

    if (!formData.location.trim()) {
      alert(
        "Please enter the pickup location."
      );
      return;
    }

    if (!formData.pickup_date || !formData.pickup_time) {
      alert(
        "Please select the pickup date and pickup time."
      );
      return;
    }

    const selectedPickupTime = new Date(
      `${formData.pickup_date}T${formData.pickup_time}:00`
    );

    if (
      Number.isNaN(selectedPickupTime.getTime()) ||
      selectedPickupTime.getTime() <= Date.now()
    ) {
      alert(
        "Pickup date and time must be in the future."
      );
      return;
    }

    if (!selectedMatch) {
      alert(
        "Please select an NGO using Donor Match or Find the Best Match."
      );
      return;
    }

    if (!donationId) {
      alert(
        "Please select Donor Match or Find the Best Match first."
      );
      return;
    }

    const ngoId =
      selectedMatch.ngo_id ||
      selectedMatch.id ||
      selectedMatch.ngo;

    const allocationQuantity =
      getSelectedQuantity();

    if (!ngoId) {
      alert(
        "Selected NGO ID is missing."
      );
      return;
    }

    if (
      allocationQuantity <= 0
    ) {
      alert(
        "No quantity can be allocated to this NGO."
      );
      return;
    }

    try {

      setLoading(true);
      setAllocationLoading(true);

      // =================================================
      // UPDATE DONATION WITH SELECTED NGO
      // =================================================

      try {

        await api.patch(
          `donation/${donationId}/`,
          {
            ngo: ngoId
          }
        );

      } catch (updateError) {

        console.warn(
          "Donation NGO update failed:",
          updateError.response?.data
        );

        /*
         * Some backends may already assign NGO
         * during allocation.
         *
         * Therefore we continue to allocation.
         */
      }

      // =================================================
      // ALLOCATE ONLY REQUIRED QUANTITY
      // =================================================

      const requirementId =
        selectedMatch.requirement_id;

      if (!requirementId) {
        throw new Error(
          "Selected NGO requirement ID is missing."
        );
      }

      const allocationResponse =
        await api.post(
          `donation/${donationId}/allocate/`,
          {
            allocations: [
              {
                requirement_id: requirementId,
                quantity: allocationQuantity
              }
            ]
          }
        );

      console.log(
        "ALLOCATION RESPONSE:",
        allocationResponse.data
      );

      // =================================================
      // CREATE PICKUP REQUEST NOW
      // =================================================
      // Donor selects the pickup schedule before NGO acceptance.
      // The pickup endpoint needs the allocation ID returned above.
      const allocationData = allocationResponse.data;

      const createdAllocation =
        allocationData?.allocations?.[0] ||
        allocationData?.results?.[0] ||
        allocationData?.data?.[0] ||
        allocationData?.allocation ||
        allocationData;

      const allocationId =
        createdAllocation?.allocation_id ||
        createdAllocation?.id;

      if (!allocationId) {
        throw new Error(
          "Donation was allocated, but the allocation ID was not returned. Pickup could not be scheduled."
        );
      }

      const pickupResponse = await api.post(
        "pickup/",
        {
          allocation_id: allocationId,
          pickup_address: formData.location.trim(),
          scheduled_time:
            `${formData.pickup_date}T${formData.pickup_time}:00`,
          notes: formData.pickup_notes.trim(),
        }
      );

      console.log(
        "PICKUP CREATED:",
        pickupResponse.data
      );

      setAllocationSuccess({
        ngoName:
          selectedMatch.ngo_name ||
          selectedMatch.name ||
          "Selected NGO",

        quantity: allocationQuantity,

        item:
          mainDetectedItem?.item ||
          formData.item_name ||
          "Donation",

        message:
          "Your donation is allocated and the pickup has already been scheduled. The NGO will accept the donation separately."
      });

    } catch (error) {

      console.error(
        "ALLOCATION ERROR:",
        error
      );

      console.error(
        "Response:",
        error.response?.data
      );

      if (
        error.response?.status === 401
      ) {

        alert(
          "Your login session has expired. Please login again."
        );

      } else if (
        error.response?.data
      ) {

        alert(
          JSON.stringify(
            error.response.data
          )
        );

      } else {

        alert(
          "Unable to allocate donation."
        );
      }

    } finally {

      setLoading(false);
      setAllocationLoading(false);
    }
  };

  // =====================================================
  // SELECTED NGO
  // =====================================================

  const selectedNGO =
    ngos.find(
      (ngo) =>
        String(ngo.id) ===
        String(formData.ngo)
    );

  // =====================================================
  // RENDER NGO CARD
  // =====================================================

  const renderNGOCard = (
    ngo,
    index
  ) => {

    const ngoId =
      ngo.ngo_id ||
      ngo.id ||
      ngo.ngo;

    const ngoName =
      ngo.ngo_name ||
      ngo.name ||
      "NGO";

    const remaining =
      ngo.remaining_need ??
      ngo.remaining_quantity ??
      ngo.required_quantity ??
      0;

    const recommended =
      ngo.recommended_quantity ??
      Math.min(
        totalQuantity,
        Number(remaining)
      );

    const priority =
      ngo.priority ||
      "Normal";

    const isSelected =
      selectedMatch &&
      String(
        selectedMatch.ngo_id ||
        selectedMatch.id ||
        selectedMatch.ngo
      ) ===
      String(ngoId);

    return (
      <div
        className={
          "matching-ngo-card " +
          (
            isSelected
              ? "selected"
              : ""
          )
        }
        key={
          ngoId ||
          index
        }
      >

        <div className="matching-ngo-top">

          <div className="matching-ngo-icon">
            🏢
          </div>

          <div>

            <h4>
              {ngoName}
            </h4>

            <span>
              {ngo.city ||
                "Approved NGO"}
            </span>

          </div>

        </div>

        <div className="matching-ngo-info">

          <div>
            <span>
              Needs
            </span>

            <strong>
              {remaining}
            </strong>
          </div>

          <div>
            <span>
              Your donation
            </span>

            <strong>
              {totalQuantity}
            </strong>
          </div>

          <div>
            <span>
              Can receive
            </span>

            <strong>
              {recommended}
            </strong>
          </div>

        </div>

        <div className="matching-ngo-bottom">

          <span
            className={
              `priority-badge priority-${String(
                priority
              ).toLowerCase()}`
            }
          >
            {priority}
          </span>

          <button
            type="button"
            onClick={() =>
              handleSelectNGO(
                ngo
              )
            }
          >
            {isSelected
              ? "✓ Selected"
              : "Select NGO"}
          </button>

        </div>

      </div>
    );
  };

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div className="donate-page">

      {/* =================================================
          HERO
      ================================================= */}

      <div className="donate-hero">

        <div>

          <span className="donate-badge">
            MAKE A DIFFERENCE ❤️
          </span>

          <h1>
            Donate smarter.
            <br />

            <span>
              Create an impact.
            </span>
          </h1>

          <p>
            Upload a photo and we'll handle the details,
            count the items and help find
            the right NGO.
          </p>

        </div>

        <div className="hero-heart">
          ✨
        </div>

      </div>


      {/* =================================================
          FORM
      ================================================= */}

      {allocationSuccess && (
        <div className="allocation-success">

          <div className="allocation-success-icon">
            ✓
          </div>

          <span className="allocation-success-badge">
            DONATION ALLOCATED
          </span>

          <h2>
            Donation Successfully Matched! 🎉
          </h2>

          <p>
            Your donation has been allocated to an NGO and your pickup
            date and time have already been scheduled. The NGO will
            process the donation separately.
          </p>

          <div className="allocation-success-details">

            <div>
              <span>ITEM</span>
              <strong>
                📦 {allocationSuccess.item}
              </strong>
            </div>

            <div>
              <span>QUANTITY</span>
              <strong>
                {allocationSuccess.quantity}
              </strong>
            </div>

            <div>
              <span>NGO</span>
              <strong>
                🏢 {allocationSuccess.ngoName}
              </strong>
            </div>

            <div className="allocation-success-pickup-message">
              <span>PICKUP</span>

              <strong>
                🚚 Pickup Scheduled
              </strong>

              <small>
                📅 {formData.pickup_date} &nbsp; 🕐 {formData.pickup_time}
              </small>
            </div>

          </div>

          <div className="allocation-success-actions">

            <button
              type="button"
              onClick={() =>
                navigate("/my-donations")
              }
            >
              📋 View My Donations
            </button>

            <button
              type="button"
              className="secondary"
              onClick={() =>
                navigate("/dashboard")
              }
            >
              ← Back to Dashboard
            </button>

          </div>

        </div>
      )}

      <form
        className="donate-form"
        onSubmit={
          handleSubmit
        }
      >

        {/* =================================================
            DONOR
        ================================================= */}

        <div className="donate-card donor-card">

          <div className="card-heading">

            <div className="heading-icon">
              👤
            </div>

            <div>

              <span>
                DONOR
              </span>

              <h2>
                Your contribution
              </h2>

            </div>

          </div>

          <div className="donor-information">

            <div className="donor-avatar">

              {donorName
                ? donorName
                    .charAt(0)
                    .toUpperCase()
                : "D"}

            </div>

            <div>

              <strong>
                {donorName ||
                  "Logged-in donor"}
              </strong>

              <span>
                {donorEmail ||
                  "Your donation account"}
              </span>

            </div>

            <div className="verified-label">
              ✓ Logged in
            </div>

          </div>

        </div>


        {/* =================================================
            IMAGE + AI
        ================================================= */}

        <div className="donate-card ai-card">

          <div className="card-heading">

            <div className="heading-icon ai-icon">
              ✨
            </div>

            <div>

              <span>
                WHAT ARE YOU DONATING?
              </span>

              <h2>
                Show us what you're donating
              </h2>

            </div>

          </div>


          {/* IMAGE UPLOAD */}

          <label
            htmlFor="item-image"
            className={
              imagePreview
                ? "upload-box has-preview"
                : "upload-box"
            }
          >

            {imagePreview ? (

              <div className="image-preview-wrapper">

                <img
                  src={imagePreview}
                  alt="Donation preview"
                />

                <div className="change-image">
                  Click to change image
                </div>

              </div>

            ) : (

              <div className="upload-content">

                <div className="upload-icon">
                  📷
                </div>

                <strong>
                  Upload a donation photo
                </strong>

                <span>
                  Snap a photo and we'll handle the details.
                </span>

                <small>
                  JPG, JPEG or PNG
                </small>

              </div>

            )}

            <input
              id="item-image"
              type="file"
              name="item_image"
              accept="image/*"
              onChange={
                handleChange
              }
            />

          </label>


          {/* ANALYZE */}

          <div className="ai-analyze-wrapper">

            <button
              type="button"
              className="ai-analyze-btn"
              onClick={
                handleAnalyzeImage
              }
              disabled={
                !formData.item_image ||
                aiLoading
              }
            >

              {aiLoading ? (

                <span
                  className="ai-loading"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "10px",
                  }}
                >

                  <span
                    className="ai-spinner"
                    aria-hidden="true"
                  />

                  <span>
                    Checking your donation... ✨
                  </span>

                  <span
                    aria-hidden="true"
                    style={{
                      display: "inline-flex",
                      gap: "2px",
                    }}
                  >
                    <span>•</span>
                    <span>•</span>
                    <span>•</span>
                  </span>

                </span>

              ) : (

                <>
                  ✨ Analyze Image
                </>

              )}

            </button>

          </div>


          {/* ERROR */}

          {aiError && (

            <div className="ai-error">
              ⚠️ {aiError}
            </div>

          )}


          {/* =================================================
              AI RESULT
          ================================================= */}

          {aiItems.length > 0 && (

            <div className="ai-result-card">

              <div className="ai-result-header">

                <div className="ai-result-icon">
                  ✨
                </div>

                <div>

                  <span>
                    LOOKS GOOD! 🎉
                  </span>

                  <h3>
                    Detected Donation Items
                  </h3>

                </div>

              </div>


              <div className="ai-total">

                <div>

                  <span>
                    ITEMS DETECTED
                  </span>

                  <strong>
                    {aiItems.length}
                  </strong>

                </div>

                <div>

                  <span>
                    TOTAL QUANTITY
                  </span>

                  <strong>
                    {totalQuantity}
                  </strong>

                </div>

              </div>


              <div className="detected-items">

                {aiItems.map(
                  (item) => {

                    const confidence =
                      item.confidence !==
                      null
                        ? Number(
                            item.confidence
                          ) <= 1
                          ? Number(
                              item.confidence
                            ) * 100
                          : Number(
                              item.confidence
                            )
                        : null;

                    return (

                      <div
                        className="detected-item"
                        key={item.id}
                      >

                        <div className="detected-item-main">

                          <div className="detected-item-icon">
                            📦
                          </div>

                          <div>

                            <h4>
                              {item.item}
                            </h4>

                            <span>
                              {item.category}
                            </span>

                          </div>

                        </div>

                        <div className="detected-quantity">

                          <span>
                            Quantity
                          </span>

                          <strong>
                            × {item.quantity}
                          </strong>

                        </div>

                        {confidence !==
                          null && (

                          <div className="confidence">

                            <div className="confidence-top">

                              <span>
                                Confidence
                              </span>

                              <strong>
                                {confidence.toFixed(
                                  1
                                )}
                                %
                              </strong>

                            </div>

                            <div className="confidence-bar">

                              <div
                                className="confidence-fill"
                                style={{
                                  width:
                                    `${Math.min(
                                      confidence,
                                      100
                                    )}%`
                                }}
                              />

                            </div>

                          </div>

                        )}

                      </div>

                    );

                  }
                )}

              </div>

              <div className="ai-note">

                ✨ Your donation is ready to go!
                Now choose where you'd like it to make an impact.

              </div>

            </div>

          )}

        </div>


        {/* =================================================
            MATCHING
        ================================================= */}

        {aiItems.length > 0 && (

          <div className="donate-card matching-card">

            <div className="card-heading">

              <div className="heading-icon">
                🎯
              </div>

              <div>

                <span>
                  NGO MATCHING
                </span>

                <h2>
                  Where should your donation go?
                </h2>

              </div>

            </div>


            {/* MATCH TABS */}

            <div className="match-tabs">

              <button
                type="button"
                className={
                  matchMode === "donor"
                    ? "match-tab active"
                    : "match-tab"
                }
                onClick={() =>
                  handleMatching(
                    "donor"
                  )
                }
                disabled={
                  matchingLoading ||
                  allocationLoading
                }
              >

                <span>
                  🧑
                </span>

                <div>

                  <strong>
                    Donor Match
                  </strong>

                  <small>
                    You choose the NGO
                  </small>

                </div>

              </button>


              <button
                type="button"
                className={
                  matchMode === "ai"
                    ? "match-tab active ai-tab"
                    : "match-tab ai-tab"
                }
                onClick={() =>
                  handleMatching(
                    "ai"
                  )
                }
                disabled={
                  matchingLoading ||
                  allocationLoading
                }
              >

                <span>
                  ✨
                </span>

                <div>

                  <strong>
                    Find the Best Match
                  </strong>

                  <small>
                    We'll find an NGO that needs it most
                  </small>

                </div>

              </button>

            </div>


            {/* DRAFT STATUS */}

            {donationId && (

              <div className="ai-note">

                ✓ Donation created.
                Now you can choose an NGO for allocation.
                Pickup will be scheduled only after NGO acceptance.

              </div>

            )}


            {/* LOADING */}

            {matchingLoading && (

              <div className="matching-loading">

                <span className="ai-spinner" />

                {matchMode === "ai"
                  ? "Finding the right place for your donation..."
                  : "Finding NGOs that need this item..."}

              </div>

            )}


            {/* ERROR */}

            {matchingError && (

              <div className="matching-error">

                ⚠️ {matchingError}

              </div>

            )}


            {/* =================================================
                RECOMMENDATION
            ================================================= */}

            {!matchingLoading &&
              matchMode === "ai" &&
              aiRecommendation && (

              <div className="ai-recommendation">

                <div className="recommendation-badge">
                  ✨ BEST MATCH FOR YOU 🏆
                </div>

                <h3>
                  {aiRecommendation.ngo_name ||
                    aiRecommendation.name ||
                    "Recommended NGO"}
                </h3>

                <p>
                  {aiRecommendation.ai_reason ||
                    "This NGO has the strongest requirement match for your donation."}
                </p>

                <div className="recommendation-details">

                  <div>

                    <span>
                      NGO needs
                    </span>

                    <strong>
                      {
                        aiRecommendation.remaining_need ??
                        aiRecommendation.required_quantity ??
                        "-"
                      }
                    </strong>

                  </div>

                  <div>

                    <span>
                      Your donation
                    </span>

                    <strong>
                      {totalQuantity}
                    </strong>

                  </div>

                  <div>

                    <span>
                      Recommended
                    </span>

                    <strong>
                      {
                        aiRecommendation.recommended_quantity ??
                        Math.min(
                          totalQuantity,
                          Number(
                            aiRecommendation.remaining_need ||
                            totalQuantity
                          )
                        )
                      }
                    </strong>

                  </div>

                </div>

                <div className="recommendation-footer">

                  <span
                    className={
                      `priority-badge priority-${String(
                        aiRecommendation.priority ||
                        "Normal"
                      ).toLowerCase()}`
                    }
                  >
                    {aiRecommendation.priority ||
                      "Normal"}
                  </span>

                  <button
                    type="button"
                    onClick={() =>
                      handleSelectNGO(
                        aiRecommendation
                      )
                    }
                  >
                    Choose This NGO →
                  </button>

                </div>

              </div>

            )}


            {/* =================================================
                DONOR MATCH NGO LIST
            ================================================= */}

            {!matchingLoading &&
              matchMode === "donor" &&
              matchingNGOs.length > 0 && (

              <div className="matching-results">

                <div className="matching-results-header">

                  <span>
                    MATCHING NGOs
                  </span>

                  <strong>
                    {matchingNGOs.length} found
                  </strong>

                </div>

                {matchingNGOs.map(
                  renderNGOCard
                )}

              </div>

            )}


            {/* =================================================
                OTHER MATCHES
            ================================================= */}

            {!matchingLoading &&
              matchMode === "ai" &&
              matchingNGOs.length > 0 && (

              <div className="matching-results">

                <div className="matching-results-header">

                  <span>
                    OTHER MATCHING NGOs
                  </span>

                  <strong>
                    {matchingNGOs.length} found
                  </strong>

                </div>

                {matchingNGOs.map(
                  renderNGOCard
                )}

              </div>

            )}


            {/* NO RESULTS */}

            {!matchingLoading &&
              matchMode &&
              !aiRecommendation &&
              matchingNGOs.length === 0 &&
              !matchingError && (

              <div className="no-matches">

                <div>
                  🔎
                </div>

                <h3>
                  No matching NGOs found
                </h3>

                <p>
                  Currently no approved NGO
                  has a requirement matching
                  this donation.
                </p>

              </div>

            )}


            {/* SELECTED */}

            {selectedMatch && (

              <div className="selected-match">

                <div className="selected-match-icon">
                  ✓
                </div>

                <div>

                  <span>
                    SELECTED NGO
                  </span>

                  <strong>
                    {selectedMatch.ngo_name ||
                      selectedMatch.name ||
                      "Selected NGO"}
                  </strong>

                </div>

                <div className="selected-match-quantity">

                  <span>
                    Quantity
                  </span>

                  <strong>
                    {getSelectedQuantity()}
                  </strong>

                </div>

              </div>

            )}

          </div>

        )}


        {/* =================================================
            PICKUP LOCATION
        ================================================= */}

        <div className="donate-card">

          <div className="card-heading">

            <div className="heading-icon coral-icon">
              📍
            </div>

            <div>

              <span>
                PICKUP LOCATION
              </span>

              <h2>
                Where should we collect your donation?
              </h2>

            </div>

          </div>

          <div className="location-choice-grid">

            <button
              type="button"
              className={
                locationMode === "registered"
                  ? "location-choice active"
                  : "location-choice"
              }
              onClick={() =>
                handleLocationModeChange("registered")
              }
            >

              <span className="location-choice-icon">
                🏠
              </span>

              <span>

                <strong>
                  Use registered location
                </strong>

                <small>
                  {registeredLocation
                    ? registeredLocation
                    : "No registered location found"}
                </small>

              </span>

            </button>

            <button
              type="button"
              className={
                locationMode === "different"
                  ? "location-choice active"
                  : "location-choice"
              }
              onClick={() =>
                handleLocationModeChange("different")
              }
            >

              <span className="location-choice-icon">
                ✏️
              </span>

              <span>

                <strong>
                  Enter a different location
                </strong>

                <small>
                  Choose another pickup location
                </small>

              </span>

            </button>

          </div>

          {locationMode === "registered" &&
          registeredLocation ? (

            <div className="location-selected">

              ✓ Using your registered location:

              <strong>
                {registeredLocation}
              </strong>

            </div>

          ) : (

            <div className="form-group location-manual-group">

              <label>
                Pickup / Location
              </label>

              <div className="location-input">

                <span>
                  📍
                </span>

                <input
                  type="text"
                  name="location"
                  placeholder="Example: Vijayawada"
                  value={formData.location}
                  onChange={handleChange}
                  required
                />

              </div>

            </div>

          )}

          {/* =================================================
              PICKUP SCHEDULE
          ================================================= */}

          <div className="pickup-schedule-card">
            <div className="pickup-schedule-heading">
              <div className="pickup-schedule-icon">
                🚚
              </div>

              <div>
                <span>
                  PICKUP SCHEDULE
                </span>

                <h3>
                  When should we collect it?
                </h3>

                <p>
                  Choose the pickup date and time now. The schedule is
                  created with your donation before NGO acceptance.
                </p>
              </div>
            </div>

            <div className="pickup-form-row">
              <div className="form-group">
                <label htmlFor="donation-pickup-date">
                  📅 Pickup Date
                </label>

                <input
                  id="donation-pickup-date"
                  type="date"
                  name="pickup_date"
                  value={formData.pickup_date}
                  min={new Date().toISOString().split("T")[0]}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="donation-pickup-time">
                  🕐 Pickup Time
                </label>

                <input
                  id="donation-pickup-time"
                  type="time"
                  name="pickup_time"
                  value={formData.pickup_time}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="donation-pickup-notes">
                📝 Pickup Notes (Optional)
              </label>

              <textarea
                id="donation-pickup-notes"
                name="pickup_notes"
                rows="3"
                value={formData.pickup_notes}
                onChange={handleChange}
                placeholder="Any instructions for the pickup..."
              />
            </div>
          </div>

        </div>


        {/* =================================================
            FINAL ACTION
        ================================================= */}

        <div className="donate-action">

          <div className="action-message">

            <span>
              ♥
            </span>

            <div>

              <strong>
                Ready to make a difference?
              </strong>

              <p>

                {selectedMatch

                  ? `Your ${getSelectedQuantity()} item${
                      getSelectedQuantity() > 1
                        ? "s"
                        : ""
                    } will be allocated to ${
                      selectedMatch.ngo_name ||
                      selectedMatch.name ||
                      "the selected NGO"
                    }.`

                  : "Analyze your image and select Donor Match or Find the Best Match."}

              </p>

            </div>

          </div>


          <button
            type="submit"
            className="donate-submit"
            disabled={
              loading ||
              ngoLoading ||
              aiItems.length === 0 ||
              !selectedMatch ||
              !donationId
            }
          >

            {loading ? (

              <>
                <span className="donate-spinner" />

                {allocationLoading
                  ? "Allocating..."
                  : "Submitting..."}

              </>

            ) : (

              <>
                Allocate Donation

                <span>
                  →
                </span>
              </>

            )}

          </button>

        </div>

      </form>

    </div>
  );
}

export default DonateItem;