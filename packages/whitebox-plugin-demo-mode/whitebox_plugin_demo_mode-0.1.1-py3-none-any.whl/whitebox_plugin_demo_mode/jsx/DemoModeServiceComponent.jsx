import { useEffect } from "react";

const { importWhiteboxStateStore, withStateStore } = Whitebox;

const DemoModeServiceComponentToWrap = () => {
  const useMissionControlStore = importWhiteboxStateStore(
    "flight.mission-control"
  );
  const flightSessions = useMissionControlStore((state) => state.flightSessions);
  const enterPlaybackMode = useMissionControlStore((state) => state.enterPlaybackMode);

  useEffect(() => {
    // Immediately on load this might not be initialized yet
    if (!flightSessions || flightSessions.length === 0)
      return;

    const demoTarget = Whitebox.utils.pluginConfig.demo_mode_flight_session_id;
    if (!demoTarget) {
      console.error("Demo mode plugin active but flight session ID not configured");
      return;
    }

    const targetSession = flightSessions.find(
      (session) => session.id === demoTarget
    );

    if (!targetSession) {
      console.error("Demo mode flight session ID not found among available sessions");
      return;
    }

    setTimeout(() => {
      console.log("Entering demo mode playback for session ID:", demoTarget);
      enterPlaybackMode(targetSession);
    }, 100);  // Slight delay to ensure app is fully ready
  }, [flightSessions]);


  // This component does not render anything visible
  return null;
}

const DemoModeServiceComponent = withStateStore(
    DemoModeServiceComponentToWrap,
    ["flight.mission-control"],
)

export { DemoModeServiceComponent };
export default DemoModeServiceComponent;
