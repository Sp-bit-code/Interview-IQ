package com.interviewiq.progress.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

@Entity
@Table(name = "study_progress")
public class StudyProgress {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Column(nullable = false)
    private String userId;

    @NotBlank
    @Column(nullable = false)
    private String topicName;

    @NotNull
    @Column(nullable = false)
    private Boolean completed;

    public StudyProgress() {
    }

    public StudyProgress(String userId, String topicName, Boolean completed) {
        this.userId = userId;
        this.topicName = topicName;
        this.completed = completed;
    }

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