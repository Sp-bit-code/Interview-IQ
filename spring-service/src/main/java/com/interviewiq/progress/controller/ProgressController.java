package com.interviewiq.progress.controller;

import com.interviewiq.progress.model.StudyProgress;
import com.interviewiq.progress.service.ProgressService;

import jakarta.validation.Valid;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/progress")
@CrossOrigin(origins = {
        "http://localhost:5173",
        "https://interview-iq-0imv.onrender.com",
        "https://interview-iq-8c6r.onrender.com"
})
public class ProgressController {

    private final ProgressService progressService;


    // ===============================
    // CONSTRUCTOR INJECTION
    // ===============================

    public ProgressController(
            ProgressService progressService
    ) {

        this.progressService = progressService;
    }


    // ===============================
    // GET USER PROGRESS
    // ===============================

    @GetMapping("/{userId}")
    public ResponseEntity<List<StudyProgress>> getUserProgress(
            @PathVariable String userId
    ) {

        List<StudyProgress> progress =
                progressService.getUserProgress(userId);

        return ResponseEntity.ok(progress);
    }


    // ===============================
    // SAVE / UPDATE PROGRESS
    // ===============================

    @PostMapping
    public ResponseEntity<StudyProgress> saveProgress(
            @Valid @RequestBody StudyProgress studyProgress
    ) {

        StudyProgress savedProgress =
                progressService.saveOrUpdateProgress(
                        studyProgress
                );

        return ResponseEntity.ok(savedProgress);
    }


    // ===============================
    // COMPLETED TOPIC COUNT
    // ===============================

    @GetMapping("/{userId}/completed-count")
    public ResponseEntity<Map<String, Long>> getCompletedTopicCount(
            @PathVariable String userId
    ) {

        long completedCount =
                progressService.getCompletedTopicCount(
                        userId
                );

        return ResponseEntity.ok(
                Map.of(
                        "completedTopics",
                        completedCount
                )
        );
    }


    // ===============================
    // DELETE PROGRESS
    // ===============================

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, String>> deleteProgress(
            @PathVariable Long id
    ) {

        progressService.deleteProgress(id);

        return ResponseEntity.ok(
                Map.of(
                        "message",
                        "Progress deleted successfully"
                )
        );
    }
}
