<?php
$inputVideo = 'https://storage.cloud.google.com/api-assignment-395306.appspot.com/pexels_videos_2077836%20(1080p).mp4'; // Update with the path to your input video file
$outputVideo = 'https://storage.cloud.google.com/'; // Update with the desired output path

// Command to convert video to 480p using FFmpeg
$ffmpegCmd = "ffmpeg -i $inputVideo -vf scale=854:480 $outputVideo";

// Execute the FFmpeg command
exec($ffmpegCmd, $output, $returnCode);

if ($returnCode === 0) {
    echo "Video converted successfully to 480p.";
} else {
    echo "Error converting video: " . implode("\n", $output);
}
?>
