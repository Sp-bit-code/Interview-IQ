package com.interviewiq.progress.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class StudyProgress {

    private Long id;

    @NotBlank
    private String userId;

    @NotBlank
    private String topicName;

    @NotNull
    private Boolean completed;


    // Default constructor
    public StudyProgress() {
    }


    // Constructor without ID
    public StudyProgress(
            String userId,
            String topicName,
            Boolean completed
    ) {
        this.userId = userId;
        this.topicName = topicName;
        this.completed = completed;
    }


    // Constructor with ID
    public StudyProgress(
            Long id,
            String userId,
            String topicName,
            Boolean completed
    ) {
        this.id = id;
        this.userId = userId;
        this.topicName = topicName;
        this.completed = completed;
    }


    // ===============================
    // GETTERS
    // ===============================

    public Long getId() {
        return id;
    }

    public String getUserId() {
        return userId;
    }

    public String getTopicName() {
        return topicName;
    }

    public Boolean getCompleted() {
        return completed;
    }


    // ===============================
    // SETTERS
    // ===============================

    public void setId(Long id) {
        this.id = id;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public void setTopicName(String topicName) {
        this.topicName = topicName;
    }

    public void setCompleted(Boolean completed) {
        this.completed = completed;
    }
}
